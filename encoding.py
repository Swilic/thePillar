import os
from image import Image
from pixel import Pixel


class Encoder:
    def __init__(self, image: 'Image'):
        self.__image = image

    def save_to(self, path: str) -> None:
        with open(path + "file.ulbmp", 'wb') as f:
            for i in self.__image:
                f.write(i)


class Decoder:
    @staticmethod
    def load_from(path: str) -> object:
        ...


if __name__ == '__main__':
    p = Pixel(34, 56, 21)
    pp = Pixel(54, 23, 76)
    image = Image(2, 2, [p, pp, p, pp])
    encoder = Encoder(image)
    encoder.save_to("/home/ahew/code/projet/thePillar/000589811/")
