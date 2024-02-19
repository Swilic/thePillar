from image import Image
from pixel import Pixel

ULBMP = b'\x55\x4c\x42\x4d\x50'


def save_v1(f, img: 'Image') -> None:
    header = ULBMP + b'\x01\x0c\x00'
    width = img.width.to_bytes(length=2, byteorder='little', signed=False)
    height = img.height.to_bytes(length=2, byteorder='little', signed=False)
    f.write(header + width + height)
    for r, g, b in img:
        f.write(r.to_bytes(length=1, byteorder='big'))
        f.write(g.to_bytes(length=1, byteorder='big'))
        f.write(b.to_bytes(length=1, byteorder='big'))


def save_v2(f, img: 'Image') -> None:
    def write(file, c: int, pix: 'Pixel'):
        c = 1 if c == 0 else c
        file.write(c.to_bytes(length=1, byteorder='big', signed=False))
        for i in range(3):
            file.write(pix.color[i].to_bytes(length=1, byteorder='big', signed=False))

    header = ULBMP + b'\x02\x0c\x00'
    width = img.width.to_bytes(length=2, byteorder='little', signed=False)
    height = img.height.to_bytes(length=2, byteorder='little', signed=False)
    f.write(header + width + height)
    count = 1
    for i in range(1, len(img)):
        if img[i] == img[i-1]:
            count += 1
        else:
            write(f, count, img[i-1])
            count = 1
        if count == 255:
            write(f, 255, img[i-1])
            count = 0
    write(f, count, img[-1])


class Encoder:
    def __init__(self, img: 'Image', version: int = 1):
        self.__image = img
        self.__version = version

    def save_to(self, path: str) -> None:
        case = {
            1: save_v1,
            2: save_v2,
        }
        with open(path, 'wb') as f:
            if 1 <= self.version <= 2:
                case[self.version](f, self.image)

    @property
    def image(self) -> 'Image':
        return self.__image

    @property
    def version(self) -> int:
        return self.__version


def verify_header(header: bytes) -> bool:
    try:
        if len(header) != 12:
            raise Exception('Header length error')
        ulbmp = header[:5]
        if ulbmp != ULBMP:
            raise Exception('Header ULBMP is not valid')
    except Exception as e:
        raise Exception(e)

    return True


def load_v1(file_list: list) -> list['Pixel']:
    pixel_list = list()
    for i in range(0, len(file_list), 3):
        pixel_list.append(Pixel(file_list[i], file_list[i + 1], file_list[i + 2]))

    return pixel_list


def load_v2(file_list: list) -> list['Pixel']:
    pixel_list = list()
    for i in range(0, len(file_list), 4):
        for j in range(int.from_bytes(file_list[i:i+1], byteorder='big', signed=False)):
            pixel_list.append(Pixel(file_list[i+1], file_list[i+2], file_list[i+3]))

    return pixel_list


def get_header_info(header: bytes) -> tuple[int, int, int]:
    version = int.from_bytes(header[5:6], byteorder='little', signed=False)
    width = int.from_bytes(header[8:10], byteorder='little', signed=False)
    height = int.from_bytes(header[10:12], byteorder='little', signed=False)
    return version, width, height


class Decoder:

    @staticmethod
    def load_from(path: str) -> 'Image':
        case = {
            1: load_v1,
            2: load_v2
        }
        with open(path, 'rb') as f:
            try:
                header = f.read(12)
                verify_header(header)
                version, width, height = get_header_info(header)
            except Exception as e:
                raise e

            file_list = list(f.read())

        list_pixel = case[version](file_list)
        return Image(width, height, list_pixel)


if __name__ == '__main__':
    BLACK = Pixel(0, 0, 0)
    WHITE = Pixel(0xFF, 0xFF, 0xFF)
    image = Image(300, 1, [BLACK]*300)
    # x = Decoder.load_from('./file.ulbmp')
    Encoder(image, 2).save_to('file.ulbmp')
    x = Decoder.load_from('file.ulbmp')
