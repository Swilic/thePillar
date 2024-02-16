import sys
import os
from image import Image
from pixel import Pixel
from encoding import Encoder, Decoder
from PySide6 import QtCore, QtWidgets, QtGui
import random


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.label = QtWidgets.QLabel()
        self.layout = QtWidgets.QVBoxLayout()
        self.setWindowTitle('Projet informatique avec 17 pages de consignes')
        self.is_image = False
        self.load_button = QtWidgets.QPushButton('Load')
        self.save_button = QtWidgets.QPushButton('Save')

        self.init_UI()

    def init_UI(self):
        self.load_button.clicked.connect(self.load)
        self.save_button.setEnabled(self.is_image)

        but_box = QtWidgets.QHBoxLayout()
        but_box.addStretch(1)

        but_box.addWidget(self.load_button, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        but_box.addWidget(self.save_button, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(self.layout)
        vbox.addLayout(but_box)

        self.setLayout(vbox)

        self.show()
    @QtCore.Slot()
    def load(self):
        photo = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', os.getcwd(), 'Images (*.ulbmp *.ULBMP)')[0]
        try:
            photo = Decoder.load_from(photo)
        except Exception as e:
            QtWidgets.QErrorMessage(self).showMessage(str(e))
        self.is_image = True
        self.image = QtGui.QImage(photo.width, photo.height, QtGui.QImage.Format_RGB32)
        for i in range(photo.width):
            for j in range(photo.height):
                r, g, b = photo[i, j].color

                value = QtGui.qRgb(r, g, b)
                self.image.setPixel(i, j, value)

        pix = QtGui.QPixmap(self.image)
        self.label.setPixmap(pix)
        self.label.setMargin(10)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.save_button.setEnabled(self.is_image)
        self.layout.addWidget(self.label)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()
    sys.exit(app.exec())
