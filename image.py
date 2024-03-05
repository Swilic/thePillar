"""
NOM : <Kazberuk>
PRÉNOM : <Denis>
SECTION : <INFO>
MATRICULE : <000589811>
"""

from pixel import Pixel


def verify_entries(width: int, height: int, pixels: list[Pixel]) -> bool:
    if width * height != len(pixels):
        raise Exception('Largeur et longueur ne correspondent pas aux nombres de pixels.')

    for elem in pixels:
        if not isinstance(elem, Pixel):
            raise Exception('La liste de pixels doit être une classe Pixel')

    return True


class Image:
    def __init__(self, width: int, height: int, pixels: list['Pixel']) -> None:
        verify_entries(width, height, pixels)
        self.__width = width
        self.__height = height
        self.__pixels = pixels
        self.__count = len(pixels)

    def __getitem__(self, pos: [tuple, int]) -> 'Pixel':  # Comment faire le double type de parametre ? surcharge
        if not self.is_valid_pos(pos):
            raise IndexError

        if isinstance(pos, int):
            return self.pixels[pos]
        elif isinstance(pos, tuple):
            return self.pixels[pos[0] + pos[1] * self.width]

    def __setitem__(self, pos: tuple, pix: 'Pixel'):
        if not self.is_valid_pos(pos):
            raise IndexError

        self.pixels[pos[1] * self.height + pos[0]] = pix

    def __str__(self):
        return f'width: {self.width}, height: {self.height}. pixels: {self.pixels}'

    def __len__(self):
        return self.__count

    def __eq__(self, other: 'Image') -> bool:
        if not isinstance(other, Image) and len(other) != self.__count:
            return False

        for i in range(len(self.pixels)):
            if self.pixels[i].color != other.pixels[i].color:
                return False
        return True

    def __iter__(self):
        for i in range(len(self.pixels)):
            yield self.pixels[i].color

    @property
    def pixels(self) -> list:
        return self.__pixels

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    def is_valid_pos(self, pos: [tuple, int]) -> bool:
        if isinstance(pos, int) and pos < len(self):
            return True
        elif isinstance(pos, tuple):
            if pos[0] + pos[1] * self.width < len(self):
                if pos[0] < self.width and pos[1] < self.height:
                    return True

        return False


if __name__ == '__main__':
    pixel = Pixel(123, 45, 87)
    pixel2 = Pixel(123, 45, 86)
    image = Image(2, 1, [pixel, pixel2])
    # image1 = Image(10, 10, [pixel2])
    print(image[0, 0])
    print(image.width, image.height)
