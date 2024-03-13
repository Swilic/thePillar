"""
NOM : <Kazberuk>
PRÉNOM : <Denis>
SECTION : <INFO>
MATRICULE : <000589811>
"""

from image import Image
from pixel import Pixel


def valid_kwarg(kwarg: dict, version: int) -> bool:
    """
    Verify if the kwarg is valid for the version 3
    :param kwarg: should contain depth and rle
    :param version: version of the file
    :return: True if the kwarg is valid or version is not 3
    """
    if version != 3:
        return True
    if kwarg['depth'] is None or kwarg['rle'] is None:
        raise ValueError('Missing depth or rle')

    return True


def get_header(img: 'Image', ver: int) -> tuple[bytes, bytes, bytes, bytes]:
    """
    Get the header for all the version
    :param img: object Image
    :param ver: version of the image
    :return: tuple with extension, header length, width and height
    """
    extension = b'ULBMP' + ver.to_bytes(length=1, byteorder='little', signed=False)
    width = img.width.to_bytes(length=2, byteorder='little', signed=False)
    height = img.height.to_bytes(length=2, byteorder='little', signed=False)
    length_h = len(extension) + len(width) + len(height) + 2
    length_h = length_h.to_bytes(length=2, byteorder='little', signed=False)

    return extension, length_h, width, height


def translate_to_byte(palette: set, depth: int, rle: bool) -> list[bytes]:
    """
    Translate the palette, depth and rle to bytes
    :param palette: palette of the image
    :param depth: depth of the image
    :param rle: rle of the image
    :return: byte list with the palette, depth and rle
    """
    list_info_v3 = [depth.to_bytes(length=1, byteorder='big', signed=False),
                    int(rle).to_bytes(length=1, byteorder='big', signed=False)]

    for tup in palette:
        for i in tup:
            list_info_v3.append(i.to_bytes(length=1, byteorder='big', signed=False))

    return list_info_v3


def get_index(palette: set, pixel: 'Pixel') -> int:
    """
    Get the index of the pixel in the palette
    :param palette: palette of the image
    :param pixel: pixel to find
    :return: index of the pixel
    """
    for i, p in enumerate(palette):
        if p == pixel:
            return i


def get_delta(pixel: 'Pixel', pixel2: 'Pixel') -> tuple[int, int, int]:
    return pixel.color[0] - pixel2.color[0], pixel.color[1] - pixel2.color[1], pixel.color[2] - pixel2.color[2]


def add_diff(diff: int, *delta: int) -> tuple[int, int, int]:
    if diff == 0:
        return small_diff(*delta)
    elif diff == 1:
        return intermediate_diff(*delta)
    elif diff == 2:
        return big_diff(*delta)


def small_diff(*delta: int) -> tuple[int, int, int]:
    dr = delta[0] + 2
    dg = delta[1] + 2
    db = delta[2] + 2
    return dr, dg, db


def intermediate_diff(*delta: int) -> tuple[int, int, int]:
    dg = delta[0] + 32
    drg = delta[1] + 8
    dbg = delta[2] + 8
    return dg, drg, dbg


def big_diff(*delta: int) -> tuple[int, int, int]:
    dr = delta[0] + 128
    dgr = delta[1] + 32
    dbr = delta[2] + 32
    return dr, dgr, dbr


def write_delta_v4(f, *delta: int) -> None:
    """
    Write the delta in the file
    :param f: file to write
    :param delta: delta to write
    :return: None
    """
    for i in delta:
        f.write(i.to_bytes(length=1, byteorder='big', signed=False))


def join_pixel_to_byte(diff: int, *delta: int):
    mi_dr_g = delta[0] >> 4
    mi_dr_d = delta[0] & 0b1111
    new = diff + mi_dr_g
    mi_dgr_g = delta[1] >> 2
    mi_dgr_d = delta[1] & 0b11
    new2 = (mi_dr_d << 4) + mi_dgr_g
    new3 = (mi_dgr_d << 6) + delta[2]
    return new, new2, new3


def save_v4(f, image: 'Image') -> None:
    extension, length_h, width, height = get_header(image, 4)
    f.write(extension + length_h + width + height)
    first_black = Pixel(0, 0, 0)
    pixel_list = [first_black] + image.pixels

    for i in range(1, len(pixel_list)):
        dr, dg, db = get_delta(pixel_list[i], pixel_list[i - 1])
        drg = dr - dg
        drb = dr - db
        dgb = dg - db
        dgr = dg - dr
        dbr = db - dr
        dbg = db - dg
        if -2 <= dr <= 2 and -2 <= dg <= 2 and -2 <= db <= 2:
            dr, dg, db = add_diff(0, dr, dg, db)

            new = (dr << 4) + (dg << 2) + db
            f.write(new.to_bytes(length=1, byteorder='big'))

        elif -32 <= dg <= 31 and -8 <= drg <= 7 and -8 <= dbg <= 7:
            dg, drg, dbg = add_diff(1, dg, drg, dbg)

            new1 = 64 + dg
            new2 = (drg << 4) + dbg
            write_delta_v4(f, new1, new2)

        elif -128 <= dr <= 127 and -32 <= dgr <= 31 and -32 <= dbr <= 31:
            dr, dgr, dbr = add_diff(2, dr, dgr, dbr)
            new, new2, new3 = join_pixel_to_byte(128, dr, dgr, dbr)

            write_delta_v4(f, new, new2, new3)

        elif -128 <= dg <= 127 and -32 <= drg <= 31 and -32 <= dbg <= 31:
            dg, drg, dbg = add_diff(2, dg, drg, dbg)
            new, new2, new3 = join_pixel_to_byte(144, dg, drg, dbg)
            write_delta_v4(f, new, new2, new3)

        elif -128 <= db <= 127 and -32 <= drb <= 31 and -32 <= dgb <= 31:
            db, drb, dgb = add_diff(2, db, drb, dgb)

            new, new2, new3 = join_pixel_to_byte(160, db, drb, dgb)
            write_delta_v4(f, new, new2, new3)

        else:
            new = 255
            new1 = pixel_list[i].color[0]
            new2 = pixel_list[i].color[1]
            new3 = pixel_list[i].color[2]
            write_delta_v4(f, new, new1, new2, new3)


class Encoder:
    def __init__(self, img: 'Image', version: int = 1, **kwargs):
        valid_kwarg(kwargs, version)
        self.__depth = kwargs.get('depth', 24)
        self.__rle = kwargs.get('rle', False)
        self.__image = img
        self.__version = version
        self.__palette = set(img.pixels)

    def save_to(self, path: str) -> None:
        case = {
            1: self.save_v1,
            2: self.save_v2,
            3: self.save_v3,
            4: save_v4,
        }
        self.f = open(path, 'wb')
        if self.version == 1:
            self.save_v1()
        elif self.version == 2:
            self.save_v2()
        elif self.version == 3:
            case[self.version]()
        elif self.version == 4:
            case[self.version](self.f, self.image)

        self.f.close()

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

    @property
    def palette(self) -> set['Pixel']:
        return self.__palette

    def save_v1(self) -> None:
        """
        Save the image for the version 1 or 3 with depth 24 and no rle
        :return: None
        """
        extension, length_h, width, height = get_header(self.image, self.version)
        self.f.write(extension + length_h + width + height)

        for r, g, b in self.image:
            self.f.write(r.to_bytes(length=1, byteorder='big'))
            self.f.write(g.to_bytes(length=1, byteorder='big'))
            self.f.write(b.to_bytes(length=1, byteorder='big'))

    def save_v2(self) -> None:
        """
        Save the image for the version 2 or 3 with depth 24 and rle
        :return: None
        """
        def write(file, c: int, pix: 'Pixel') -> None:
            """
            Write the pixel in the file
            :param file: file to write
            :param c: count of the pixel
            :param pix: pixel to write
            :return:
            """
            c = 1 if c == 0 else c
            file.write(c.to_bytes(length=1, byteorder='big', signed=False))
            for i in range(3):
                file.write(pix.color[i].to_bytes(length=1, byteorder='big', signed=False))

        extension, length_h, width, height = get_header(self.image, self.version)
        self.f.write(extension + length_h + width + height)
        count = 1
        for i in range(1, len(self.image)):
            if self.image[i] == self.image[i - 1]:
                count += 1
            else:
                write(self.f, count, self.image[i - 1])
                count = 1
            if count == 255:
                write(self.f, 255, self.image[i - 1])
                count = 0
        write(self.f, count, self.image[-1])

    def save_v3_rle(self):
        match self.depth:
            case 8:
                return self.save_v3_8_rle( )
            case 24:
                return self.save_v2()

    def save_v3_8_rle(self):
        """
        Save the image for the version 3 with depth 8 and rle
        :param f: file to write
        :param image: image to write
        :param args: should contain palette, depth and rle
        :return:
        """

        def write(file, c: int, pix: 'Pixel') -> None:
            """
            Write the pixel in the file
            :param file: file to write
            :param c: count of the pixel
            :param pix: pixel to write
            :return: None
            """
            c = 1 if c == 0 else c
            file.write(c.to_bytes(length=1, byteorder='big', signed=False))
            file.write(get_index(self.palette, pix).to_bytes(length=1, byteorder='big', signed=False))

        self.write_header_v3()
        count = 1
        for i in range(1, len(self.image)):
            if self.image[i - 1] == self.image[i]:
                count += 1
            else:
                write(self.f, count, self.image[i - 1])
                count = 1
            if count == 255:
                write(self.f, 255, self.image[i - 1])
                count = 0
        write(self.f, count, self.image[-1])

    def save_v3_1to8(self) -> None:
        self.write_header_v3()

        for i in range(0, len(self.image), 8 // self.depth):

            indexs = 0
            for j in range(8 // self.depth):
                if i + j < len(self.image):
                    index = get_index(self.palette, self.image[i + j])
                    indexs += index << (8 - self.depth * (j + 1))

            self.f.write(indexs.to_bytes(length=1, byteorder='big', signed=False))

    def write_header_v3(self) -> None:
        """
        Write the header for the version 3
        :return: None
        """
        extension, length_h, width, height = get_header(self.image, 3)
        full_length_h = int.from_bytes(length_h, byteorder='little', signed=False) + len(self.palette) * 3 + 2
        full_length_h = full_length_h.to_bytes(length=2, byteorder='little', signed=False)
        to_write = translate_to_byte(self.palette, self.depth, self.rle)
        self.f.write(extension + full_length_h + width + height)
        for i in range(0, len(to_write)):
            self.f.write(to_write[i])

    def save_v3(self) -> None:
        self.__palette = set(self.image)

        if self.rle:
            return self.save_v3_rle()
        elif not self.rle and self.depth == 24:
            return self.save_v1()
        elif self.depth <= 8:
            # no rle as the definition
            return self.save_v3_1to8()


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


def set_pixel_v3_no_rle_1to8(file_list, *arg, **k) -> list['Pixel']:
    dic, byts, length = arg
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


def load_v3_rle(file_list, *arg) -> list['Pixel']:
    dic, byts, length = arg

    if dic['depth'] == 24:
        pixel_list = load_with_rle(file_list[2:])
    elif dic['depth'] == 8:
        pixel_list = set_v3_rle_8(file_list, dic, byts, length)
    else:
        raise NotImplementedError

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
        pixel_list = load_v3_rle(file_list, dic, byts, length)

    return pixel_list


def get_color_from_byte_v4(diff: int, file_list, i: int) -> tuple[int, int, int]:
    if diff == 0:
        return color_from_small_diff(file_list, i)
    elif diff == 1:
        return color_from_intermediate_diff(file_list, i)
    elif diff == 2:
        return color_from_big_diff(file_list, i)


def color_from_small_diff(file_list, i: int) -> tuple[int, int, int]:
    r = -2 + ((file_list[i] & 0b00110000) >> 4)
    g = -2 + ((file_list[i] & 0b00001100) >> 2)
    b = -2 + (file_list[i] & 0b00000011)

    return r, g, b


def color_from_intermediate_diff(file_list, i: int) -> tuple[int, int, int]:
    dg = -32 + (file_list[i] & 0b00111111)
    dr = -8 + ((file_list[i + 1] & 0b11110000) >> 4)
    db = -8 + (file_list[i + 1] & 0b00001111)
    return dg, dr, db


def color_from_big_diff(file_list, i: int) -> tuple[int, int, int]:
    drg = (file_list[i] & 0b00001111) << 4
    dr = -128 + (drg + ((file_list[i + 1] & 0b11110000) >> 4))
    dgrd = (file_list[i + 1] & 0b00001111) << 2
    dg = -32 + (dgrd + ((file_list[i + 2] & 0b11000000) >> 6))
    db = (-32 + (file_list[i + 2] & 0b00111111))

    return dr, dg, db


def load_v4(file_list) -> list['Pixel']:
    pixel_list = [Pixel(0, 0, 0)]
    i = 0
    while i < len(file_list):
        actual = pixel_list[-1]
        actual_r, actual_g, actual_b = actual.color
        did = False

        diff = (file_list[i] & 0b10000000) >> 7
        if diff == 0:
            diff = (file_list[i] & 0b11000000) >> 6

            if diff == 0:
                # SMALL_DIFF
                r, g, b = get_color_from_byte_v4(0, file_list, i)

                pixel_list.append(Pixel(actual_r + r, actual_g + g, actual_b + b))

            elif diff == 1:
                # INTERMEDIATE_DIFF
                dg, dr, db = get_color_from_byte_v4(1, file_list, i)
                r = actual_r + dg + dr
                g = actual_g + dg
                b = actual_b + dg + db

                pixel_list.append(Pixel(r, g, b))
                i += 1
            did = True

        diff = (file_list[i] & 0b11110000) >> 4
        if not did:
            if diff == 8:
                # BIG_DIFF_R
                dr, dg, db = get_color_from_byte_v4(2, file_list, i)

                r = actual_r + dr
                g = actual_g + dr + dg
                b = actual_b + dr + db
                pixel_list.append(Pixel(r, g, b))
                i += 2

            elif diff == 9:
                # BIG_DIFF_G
                dg, dr, db = get_color_from_byte_v4(2, file_list, i)

                r = actual_r + dg + dr
                g = actual_g + dg
                b = actual_b + dg + db
                pixel_list.append(Pixel(r, g, b))
                i += 2

            elif diff == 10:
                # BIG_DIFF_B
                db, dr, dg = get_color_from_byte_v4(2, file_list, i)

                r = actual_r + db + dr
                g = actual_g + db + dg
                b = actual_b + db

                pixel_list.append(Pixel(r, g, b))
                i += 2

            elif diff == 15:
                # NEW_PIXEL
                r = file_list[i + 1]
                g = file_list[i + 2]
                b = file_list[i + 3]
                pixel_list.append(Pixel(r, g, b))
                i += 3
        i += 1

    return pixel_list[1:]


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
            4: load_v4,
        }
        with open(path, 'rb') as f:
            try:
                version, length_header, width, height = get_header_info(f)
            except Exception as e:
                raise e
            file_list = f.read()

        if 1 <= version <= 2 or version == 4:
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
    y = Decoder.load_from('./imgs/checkers3_no_rle.ulbmp')
    Encoder(y, 3, depth=8, rle=True).save_to('./file.ulbmp')
    x = Decoder.load_from('./file.ulbmp')
    # Encoder(x, 3, depth=24, rle=False).save_to('file.ulbmp')
