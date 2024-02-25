from image import Image
from pixel import Pixel


def valid_kwarg(kwarg: dict, version: int) -> bool:
    if version != 3:
        return True
    if kwarg.get('depth') is None or kwarg.get('rle') is None:
        raise ValueError('Missing depth or rle')


def get_header(img: 'Image', ver: int) -> tuple[bytes, bytes, bytes, bytes]:
    extension = b'ULBMP' + ver.to_bytes(length=1, byteorder='little', signed=False)
    width = img.width.to_bytes(length=2, byteorder='little', signed=False)
    height = img.height.to_bytes(length=2, byteorder='little', signed=False)
    length_h = len(extension) + len(width) + len(height) + 2
    length_h = length_h.to_bytes(length=2, byteorder='little', signed=False)

    return extension, width, height, length_h


def save_v1(f, img: 'Image') -> None:
    extension, width, height, length_h = get_header(img, 1)
    f.write(extension + length_h + width + height)

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

    extension, width, height, length_h = get_header(img, 2)
    f.write(extension + length_h + width + height)
    count = 1
    for i in range(1, len(img)):
        if img[i] == img[i - 1]:
            count += 1
        else:
            write(f, count, img[i - 1])
            count = 1
        if count == 255:
            write(f, 255, img[i - 1])
            count = 0
    write(f, count, img[-1])


def get_index(palette: set, pixel: 'Pixel') -> int:
    for i, p in enumerate(palette):
        if p == pixel:
            return i


def translate_to_byte(palette: set, depth: int, rle: bool) -> list[bytes]:
    l = [depth.to_bytes(length=1, byteorder='big', signed=False),
         int(rle).to_bytes(length=1, byteorder='big', signed=False)]

    for tup in palette:
        for i in tup:
            l.append(i.to_bytes(length=1, byteorder='big', signed=False))

    return l


def save_v3(f, image: 'Image', **kwargs) -> None:
    # à mettre dans une fonction!
    head = get_header(image, 3)
    palette = set(image)
    depth = kwargs.get('depth')
    rle = kwargs.get('rle')
    length_h = int.from_bytes(head[3], byteorder='little', signed=False) + len(palette) * 3 + 2
    length_h = length_h.to_bytes(length=2, byteorder='little', signed=False)
    to_write = translate_to_byte(palette, depth, rle)
    f.write(head[0] + length_h + head[1] + head[2])
    for i in range(0, len(to_write)):
        f.write(to_write[i])

    for i in range(0, len(image) - 1, 8):
        indexs = 0
        for j in range(8 // depth):
            if i + j < len(image):
                index = get_index(palette, image[i + j])
                indexs += index << (8 - depth * (j + 1))

        f.write(indexs.to_bytes(length=depth, byteorder='big', signed=False))


class Encoder:
    def __init__(self, img: 'Image', version: int = 1, **kwargs):
        valid_kwarg(kwargs, version)
        self.__depth = kwargs.get('depth', 24)
        self.__rle = kwargs.get('rle', False)
        self.__image = img
        self.__version = version

    def save_to(self, path: str) -> None:
        case = {
            1: save_v1,
            2: save_v2,
            3: save_v3,
        }
        with open(path, 'wb') as f:
            if 1 <= self.version <= 2:
                case[self.version](f, self.image)
            else:
                case[self.version](f, self.image, depth=self.depth, rle=self.rle)

    @property
    def image(self) -> 'Image':
        return self.__image

    @property
    def version(self) -> int:
        return self.__version

    @property
    def depth(self) -> int:
        return self.__depth

    @property
    def rle(self) -> bool:
        return self.__rle


def verify_header(ulbmp: bytes) -> bool:
    try:
        if ulbmp != b'ULBMP':
            raise Exception('Header ULBMP is not valid')
    except Exception as e:
        raise Exception(e)

    return True


def load_basic_rgb(file_list) -> list['Pixel']:
    pixel_list = []
    for i in range(0, len(file_list), 3):
        pixel_list.append(Pixel(file_list[i], file_list[i + 1], file_list[i + 2]))

    return pixel_list


def load_with_rle(file_list) -> list['Pixel']:
    pixel_list = []

    for i in range(0, len(file_list), 4):
        for j in range(file_list[i]):

            pixel_list.append(Pixel(file_list[i + 1], file_list[i + 2], file_list[i + 3]))

    return pixel_list


def set_v3_rle_8(file_list, *dic) -> list['Pixel']:
    dic, byts, length = dic
    pixel_list = []
    for i in range(length - 12, len(file_list), 2):
        for j in range(file_list[i]):
            index = file_list[i + 1]
            pixel_list.append(byts[index].copy())

    return pixel_list


def set_pixel_v3_no_rle_1to8(file_list, *dic, **k) -> list['Pixel']:
    dic, byts, length = dic
    pixel_list = []
    number_decal = 2 ** dic['depth'] - 1
    for i in range(len(file_list)):
        counter = 8 - dic['depth']
        pix_file = file_list[i]

        j = 0
        while j < 8 // dic['depth'] and len(pixel_list) < (k['width'] * k['height']):
            index = (pix_file & (number_decal << counter)) >> counter
            counter -= dic['depth']
            pixel_list.append(byts[index].copy())
            j += 1

    return pixel_list


def load_v3(file_list, **k) -> list['Pixel']:
    dic, byts, length = get_header_info_v3(file_list, k['lh'])

    pixel_list = []
    if not dic['rle']:
        if dic['depth'] <= 8:
            pixel_list = set_pixel_v3_no_rle_1to8(file_list[length - 12:], dic, byts, length, lh=k['lh'],
                                                  width=k['width'], height=k['height'])

        elif dic['depth'] == 24:
            pixel_list = load_basic_rgb(file_list[2:])
    else:
        pixel_list = load_v3_rle(file_list[2:], dic, byts, length)

    return pixel_list


def load_v3_rle(file_list, *arg) -> list['Pixel']:
    dic, byts, length = arg

    if dic['depth'] == 24:
        pixel_list = load_with_rle(file_list)
    elif dic['depth'] == 8:
        pixel_list = set_v3_rle_8(file_list, dic, byts, length)
    else:
        raise NotImplementedError

    return pixel_list


def get_header_info_v3(f, length: int) -> tuple[dict, list['Pixel'], int]:
    dic = {'depth': int(f[0]), 'rle': bool(f[1])}
    list_header_pixel = []
    for i in range(2, length - 14, 3):
        r = f[i]
        g = f[i + 1]
        b = f[i + 2]
        list_header_pixel.append(Pixel(r, g, b))

    return dic, list_header_pixel, length


def get_header_info(f) -> tuple[int, int, int, int]:
    ulbmp = f.read(5)
    verify_header(ulbmp)
    version = int.from_bytes(f.read(1), byteorder='little', signed=False)
    length_header = int.from_bytes(f.read(2), byteorder='little', signed=False)
    width = int.from_bytes(f.read(2), byteorder='little', signed=False)
    height = int.from_bytes(f.read(2), byteorder='little', signed=False)

    return version, length_header, width, height


class Decoder:
    @staticmethod
    def load_from(path: str) -> 'Image':
        case = {
            1: load_basic_rgb,
            2: load_with_rle,
            3: load_v3,
        }
        with open(path, 'rb') as f:
            try:
                version, length_header, width, height = get_header_info(f)
            except Exception as e:
                raise e
            file_list = f.read()

        if 1 <= version <= 2:
            list_pixel = case[version](file_list)
        else:
            list_pixel = case[version](file_list, lh=length_header, width=width, height=height)
        return Image(width, height, list_pixel)


if __name__ == '__main__':
    BLACK = Pixel(0, 0, 0)
    WHITE = Pixel(0xFF, 0xFF, 0xFF)
    image = Image(1, 1, [BLACK])
    # x = Decoder.load_from('./imgs/gradients3_rle.ulbmp')
    # with open('./file.ulbmp', 'wb') as f:
    #     f.write(bytes.fromhex('554c424d50031700030001000200ff000000ff000000ff84'))
    #
    x = Decoder.load_from('./imgs/house3_rle.ulbmp')
    # Encoder(x, 3, depth=1, rle=False).save_to('file.ulbmp')
