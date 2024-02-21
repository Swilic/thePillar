def is_valid_color(r: int, g: int, b: int):
    try:
        r = int(r)
        g = int(g)
        b = int(b)
    except Exception as e:
        raise Exception(e)

    if not (0 <= r < 256):
        raise Exception('La couleur rouge doit se trouver entre 0 et 255')
    if not (0 <= g < 256):
        raise Exception('La couleur verte doit se trouver entre 0 et 255')
    if not (0 <= b < 256):
        raise Exception('La couleur bleue doit se trouver entre 0 et 255')


class Pixel:
    def __init__(self, r: int, g: int, b: int):
        is_valid_color(r, g, b)
        self.__red = r
        self.__green = g
        self.__blue = b

    def __str__(self) -> str:
        return f'{self.__red, 16} {self.__green, 16} {self.__blue, 16}'

    def __eq__(self, other) -> bool:
        return self.__red == other.__red and self.__green == other.__green and self.__blue == other.__blue

    def __ne__(self, other) -> bool:
        return not (self == other)

    @property
    def color(self):
        return self.__red, self.__green, self.__blue

    def __copy__(self):
        return Pixel(self.color[0], self.color[1], self.color[2])


if __name__ == "__main__":
    pixel = Pixel(0x02, 255, 56)
    pix = Pixel(45, 32, 55)
    print(pixel.color)
