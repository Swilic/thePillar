from pixel import Pixel


def verify_entries(width: int, height: int, pixels: list[Pixel]) -> int:
    if width * height != len(pixels):
        raise Exception('Largeur et longueur ne correspondent pas aux nombres de pixels.')

    for elem in pixels:
        if not isinstance(elem, Pixel):
            raise Exception('La liste de pixels doit être une classe Pixel')


class Image:
    def __init__(self, width: int, height: int, pixels: list[Pixel]) -> None:
        verify_entries(width, height, pixels)

        self.__width = width
        self.__height = height
        self.__pixels = pixels
        self.__count = len(pixels)

    def __getitem__(self, pos: tuple) -> object:
        if not self.is_valid_pos(pos):
            raise IndexError
        return self.__pixels[pos[0] + pos[1] * self.__width]

    def __setitem__(self, pos: tuple, pixel: Pixel):
        if not self.is_valid_pos(pos):
            raise IndexError

        self.__pixels[pos[1] * self.__height + pos[0]] = pixel

    def __str__(self):
        return f'width: {self.__width}, height: {self.__height}. pixels: {self.__pixels}'

    def __len__(self):
        return self.__count

    def __eq__(self, other: 'Image') -> bool:
        if not isinstance(other, Image) and len(other) != self.__count:
            return False

        for i in range(len(self.__pixels)):
            if self.__pixels[i].color != other.__pixels[i].color:
                return False
        return True

    def __iter__(self):
        for i in range(len(self.__pixels)):
            yield self.__pixels[i].color

    def is_valid_pos(self, pos: tuple) -> bool:
        if pos[0] + pos[1] * self.__width < self.__count:
            if pos[0] < self.__width and pos[1] < self.__height:
                return True
        return False


if __name__ == '__main__':
    pixel = Pixel(123, 45, 87)
    pixel2 = Pixel(123, 45, 86)
    image = Image(2, 1, [pixel, pixel2])
    # image1 = Image(10, 10, [pixel2])
    print(image[0, 0])
