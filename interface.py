import sys
from image import Image
from pixel import Pixel
from encoding import Encoder, Decoder
from PySide6 import QtCore, QtWidgets, QtGui
import random


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        photo = Decoder.load_from('./imgs/checkers1.ulbmp')
        self.is_image = False
        self.image = QtGui.QImage(photo.width, photo.height, QtGui.QImage.Format_RGB32)
        for i in range(photo.width):
            for j in range(photo.height):
                r, g, b = photo[i, j].color

                value = QtGui.qRgb(r, g, b)
                self.image.setPixel(i, j, value)

        pix = QtGui.QPixmap(self.image)
        self.label = QtWidgets.QLabel()
        self.label.setPixmap(pix)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)


    # def init_UI(self):
    #     image = QtGui.QImage(3, 3, QtGui.QImage.Format_RGB32)
    #     value = QtGui.qRgb(189, 149, 39)  # 0xffbd9527
    #     image.setPixel(1, 1, value)
    #     value = QtGui.qRgb(122, 163, 39)  # 0xff7aa327
    #     image.setPixel(0, 1, value)
    #     image.setPixel(1, 0, value)
    #     value = QtGui.qRgb(237, 187, 51)  # 0xffedba31
    #     image.setPixel(2, 1, value)
    #
    #
    #     load_button = QtWidgets.QPushButton('Load')
    #     save_button = QtWidgets.QPushButton('Save')
    #     save_button.setEnabled(self.is_image)
    #
    #     but_box = QtWidgets.QHBoxLayout()
    #     but_box.addStretch(1)
    #
    #     but_box.addWidget(load_button)
    #     but_box.addWidget(save_button)
    #
    #     vbox = QtWidgets.QVBoxLayout()
    #     vbox.addStretch(1)
    #     vbox.addLayout(but_box)
    #
    #     self.setLayout(vbox)
    #
    #     self.setGeometry(300, 800, 300, 150)
    #     self.show()

    @QtCore.Slot()
    def magic(self):
        self.text.setText(random.choice(self.hello))


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()
    sys.exit(app.exec())
