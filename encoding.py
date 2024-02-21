from typing import Tuple

from image import Image
from pixel import Pixel


def valid_kwarg(kwarg: dict, version: int) -> bool:
    if version != 3:
        return True
    if kwarg.get('depth') is None or kwarg.get('rle') is None:
        raise ValueError('Missing depth or rle')


def set_v1_v2_header(img: 'Image', version: int) -> bytes:
    header = b'ULBMP' + version.to_bytes(length=1, byteorder='little', signed=False) + b'\x0c\x00'
    width = img.width.to_bytes(length=2, byteorder='little', signed=False)
    height = img.height.to_bytes(length=2, byteorder='little', signed=False)
    return header + width + height


def get_header(img: 'Image', ver: int) -> bytes:
    if 1 <= ver <= 2:
        return set_v1_v2_header(img, ver)
    elif ver == 3:
        ...


def save_v1(f, img: 'Image') -> None:
    f.write(get_header(img, 1))

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

    f.write(get_header(img, 2))
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


def save_v3():
    ...


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
            case[self.version](f, self.image)

    @property
    def image(self) -> 'Image':
        return self.__image

    @property
    def version(self) -> int:
        return self.__version


def verify_header(ulbmp: bytes) -> bool:
    try:
        if ulbmp != b'ULBMP':
            raise Exception('Header ULBMP is not valid')
    except Exception as e:
        raise Exception(e)

    return True


def load_v1(file_list) -> list['Pixel']:

    pixel_list = list()
    for i in range(0, len(file_list), 3):
        pixel_list.append(Pixel(file_list[i], file_list[i + 1], file_list[i + 2]))

    return pixel_list


def load_v2(file_list) -> list['Pixel']:
    pixel_list = list()
    for i in range(0, len(file_list), 4):
        for j in range(int.from_bytes(file_list[i:i+1], byteorder='big', signed=False)):
            pixel_list.append(Pixel(file_list[i+1], file_list[i+2], file_list[i+3]))

    return pixel_list


def load_v3(file_list, **k) -> list['Pixel']:
    dic, byts = get_header_info_v3(file_list, k['lh'])
    for i in range(len(byts) + len(dic), len(file_list)): # comprendre comment faire et faire HAHAhaahahaHahaHAAHAAHAAHAH j'suis trop drôle le soir moi. Vraiment je m'aime de trop. Imagine, non mais imagine quand même. xoxo
        print(file_list[i].to_bytes(length=1, byteorder='big', signed=False))


def get_header_info_v3(f, length: int) -> Tuple[dict, list['Pixel']]:
    dic = {'depth': f[0], 'rle': f[1]}
    list_h_pixel = []
    for i in range(2, length, 3):
        r = f[i]
        g = f[i+1]
        b = f[i+2]
        list_h_pixel.append(Pixel(r, g, b))

    return dic, list_h_pixel


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
            1: load_v1,
            2: load_v2,
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
            list_pixel = case[version](file_list, lh=length_header)
        return Image(width, height, list_pixel)


if __name__ == '__main__':
    BLACK = Pixel(0, 0, 0)
    WHITE = Pixel(0xFF, 0xFF, 0xFF)
    image = Image(1, 1, [BLACK])
    # x = Decoder.load_from('./imgs/checkers2.ulbmp')
    x = Decoder.load_from('./imgs/checkers3_no_rle.ulbmp')
    # Encoder(x, 3, depth=1, rle=False).save_to('file.ulbmp')
