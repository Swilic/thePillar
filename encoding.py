import struct

from image import Image
from pixel import Pixel
import os


class Encoder:
    def __init__(self, image: 'Image'):
        self.__image = image

    def save_to(self, path: str) -> None:
        with open(path, 'wb') as f:
            version1 = b'\x55\x4c\x42\x4d\x50\x01'
            lengthHeader = b'\x0c\x00'
            width = self.__image.width.to_bytes(length=2, byteorder='little', signed=False)
            height = self.__image.height.to_bytes(length=2, byteorder='little', signed=False)
            f.write(version1)
            f.write(lengthHeader)
            f.write(width + height)
            for r, g, b in self.__image:
                f.write(r.to_bytes(length=1, byteorder='big'))
                f.write(g.to_bytes(length=1, byteorder='big'))
                f.write(b.to_bytes(length=1, byteorder='big'))


class Decoder:
    @staticmethod
    def load_from(path: str) -> object:
        ...


if __name__ == '__main__':
    BLACK = Pixel(0, 0, 0)
    WHITE = Pixel(0xFF, 0xFF, 0xFF)
    image = Image(2, 2, [BLACK, WHITE, BLACK, WHITE])
    encoder = Encoder(image)
    print(os.getcwd())
    encoder.save_to(os.getcwd()+'/file.ulbmp')
