import os
from image import Image
from pixel import Pixel
import os


class Encoder:
    def __init__(self, image: 'Image'):
        self.__image = image

    def save_to(self, path: str) -> None:
        with open(path + "file.ulbmp", 'wb') as f:
            f.write('\x55\x4c\x42\x4d\x50\x01\x0c\x00\x02\x00\x02\x00'.encode())
            f.write('\x00\x00\x00'.encode())
            f.write('\x0D\xFF\xFF\xFF'.encode())
            f.write('\x00\x00\x00'.encode())
            f.write('\xFF\xFF\xff'.encode())


class Decoder:
    @staticmethod
    def load_from(path: str) -> object:
        ...


if __name__ == '__main__':
    p = Pixel(34, 56, 21)
    pp = Pixel(54, 23, 76)
    image = Image(2, 2, [p, pp, p, pp])
    encoder = Encoder(image)
    encoder.save_to(os.getcwd()+'/00589811')
