from encoding import Encoder, Decoder
import os
print(os.listdir('./imgs/'))
# for file in os.listdir('./imgs/'):
#     try:
#         x = Decoder.load_from('./imgs/' + file)
#         Encoder(x, 1, ).save_to('./file.ulbmp')
#         Decoder.load_from('./file.ulbmp')
#         print('version 1')
#
#         x = Decoder.load_from('./imgs/' + file)
#         Encoder(x, 2, rle=False).save_to('./file.ulbmp')
#         Decoder.load_from('./file.ulbmp')
#         print('version 2')
#
#         x = Decoder.load_from('./imgs/' + file)
#         Encoder(x, 2, rle=True).save_to('./file.ulbmp')
#         Decoder.load_from('./file.ulbmp')
#         print('version 2 rle')
#
#         x = Decoder.load_from('./imgs/' + file)
#         Encoder(x, 3, depth=1, rle=True).save_to('./file.ulbmp')
#         Decoder.load_from('./file.ulbmp')
#         print('version 3 rle 1')
#
#         x = Decoder.load_from('./imgs/' + file)
#         Encoder(x, 3, depth=2, rle=True).save_to('./file.ulbmp')
#         Decoder.load_from('./file.ulbmp')
#         print('version 3 rle 2')
#
#         x = Decoder.load_from('./imgs/' + file)
#         Encoder(x, 3, depth=4, rle=True).save_to('./file.ulbmp')
#         Decoder.load_from('./file.ulbmp')
#         print('version 3 rle 4')
#
#         x = Decoder.load_from('./imgs/' + file)
#         Encoder(x, 3, depth=8, rle=True).save_to('./file.ulbmp')
#         Decoder.load_from('./file.ulbmp')
#         print('version 3 rle 8')
#
#         x = Decoder.load_from('./imgs/' + file)
#         Encoder(x, 3, depth=24, rle=True).save_to('./file.ulbmp')
#         Decoder.load_from('./file.ulbmp')
#         print('version 3 rle 24')
#
#         x = Decoder.load_from('./imgs/' + file)
#         Encoder(x, 3, depth=1, rle=False).save_to('./file.ulbmp')
#         Decoder.load_from('./file.ulbmp')
#         print('version 3 no 1')
#
#         x = Decoder.load_from('./imgs/' + file)
#         Encoder(x, 3, depth=2, rle=False).save_to('./file.ulbmp')
#         Decoder.load_from('./file.ulbmp')
#         print('version 3 no 2')
#
#         x = Decoder.load_from('./imgs/' + file)
#         Encoder(x, 3, depth=4, rle=False).save_to('./file.ulbmp')
#         Decoder.load_from('./file.ulbmp')
#         print('version 3 no 4')
#         print('allor?')
#         x = Decoder.load_from('./imgs/' + file)
#         Encoder(x, 3, depth=8, rle=False).save_to('./file.ulbmp')
#         Decoder.load_from('./file.ulbmp')
#         print('version 3 no 8')
#
#         x = Decoder.load_from('./imgs/' + file)
#         Encoder(x, 3, depth=24, rle=False).save_to('./file.ulbmp')
#         Decoder.load_from('./file.ulbmp')
#         print('version 3 no 24')
#
#         x = Decoder.load_from('./imgs/' + file)
#         Encoder(x, 4, depth=24, rle=True).save_to('./file.ulbmp')
#         Decoder.load_from('./file.ulbmp')
#         print('version 4 rle 24')
#
#     except NotImplementedError:
#         print('NotImplementedError')
#     except ValueError:
#         print(file)


for i in os.listdir('./imgs/'):
    for j in [1, 2, 4]:
        try:
            x = Decoder.load_from('./imgs/' + i)
            Encoder(x, j, rle=True).save_to('./file.ulbmp')
            Decoder.load_from('./file.ulbmp')
            print('version', j, 'rle')
        except Exception as e:
            if e != 'Impossible de convertir la palette en profondeur demandée':
                print(e, ' ', i)
                print('version', j, 'rle')

        try:
            x = Decoder.load_from('./imgs/' + i)
            Encoder(x, j, rle=False).save_to('./file.ulbmp')
            Decoder.load_from('./file.ulbmp')
            print('version', j, 'no rle')
        except Exception as e:
            if e != 'Impossible de convertir la palette en profondeur demandée':
                print(e, ' ', i)
                print('version', j, 'rle')

    for j in [1, 2, 4, 8, 24]:
        try:
            x = Decoder.load_from('./imgs/' + i)
            Encoder(x, 3, depth=j, rle=True).save_to('./file.ulbmp')
            Decoder.load_from('./file.ulbmp')
            print('version 3 rle', j)
        except Exception as e:
            if e != 'Impossible de convertir la palette en profondeur demandée':
                print(e, ' ', i)
                print('version', j, 'rle')

        try:
            x = Decoder.load_from('./imgs/' + i)
            Encoder(x, 3, depth=j, rle=False).save_to('./file.ulbmp')
            Decoder.load_from('./file.ulbmp')
            print('version 3 no rle', j)
        except Exception as e:
            if e != 'Impossible de convertir la palette en profondeur demandée':
                print(e, ' ', i)
                print('version', j, 'rle')
