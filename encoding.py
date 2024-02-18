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
    header = ULBMP + b'\x02\x0c\x00'
    width = img.width.to_bytes(length=2, byteorder='little', signed=False)
    height = img.height.to_bytes(length=2, byteorder='little', signed=False)
    f.write(header + width + height)
    count = 1
    for i in range(1, len(img)):
        if img[i] == img[i-1]:
            count += 1
        else:
            f.write(count.to_bytes(length=1, byteorder='little', signed=False))
            [f.write(j.to_bytes(length=1, byteorder='little', signed=False)) for j in img[i-1].color]
            count = 1
    f.write(count.to_bytes(length=1, byteorder='little', signed=False))
    [f.write(j.to_bytes(length=1, byteorder='little', signed=False)) for j in img[i - 1].color]


class Encoder:
    def __init__(self, img: 'Image'):
        self.__image = img

    @property
    def image(self) -> 'Image':
        return self.__image

    def save_to(self, path: str, v=1) -> None:
        case = {
            1: save_v1,
            2: save_v2,
        }
        with open(path, 'wb') as f:
            if 1 <= v <= 2:
                case[v](f, self.image)


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


def load_v1(file_list: list) -> list[Pixel]:
    pixel_list = list()
    for i in range(0, len(file_list), 3):
        pixel_list.append(Pixel(file_list[i], file_list[i + 1], file_list[i + 2]))

    return pixel_list


def load_v2(file_list: list) -> list[Pixel]:
    pixel_list = list()
    for i in range(0, len(file_list), 4):
        for j in range(int.from_bytes(file_list[i:i+1], byteorder='little', signed=False)):
            pixel_list.append(Pixel(file_list[i+1], file_list[i+2], file_list[i+3]))

    return pixel_list


def get_header_info(header: bytes) -> tuple[int, int, int]:
    x = int.from_bytes(header[5:6], byteorder='little', signed=False)
    y = int.from_bytes(header[8:10], byteorder='little', signed=False)
    z = int.from_bytes(header[10:12], byteorder='little', signed=False)
    return x, y, z


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
    image = Image(2, 2, [BLACK, WHITE, BLACK, WHITE])
    x = Decoder.load_from('./file.ulbmp')
    Encoder(x).save_to('file.ulbmp', 2)
