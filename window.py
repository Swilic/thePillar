import sys
import os
from encoding import Encoder, Decoder
from PySide6 import QtCore, QtWidgets, QtGui


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Projet informatique avec 17(dix-sept)pages de consignes')
        self.is_image = False
        self.image = None
        self.Qimage = QtGui.QImage()

        self.label = QtWidgets.QLabel()
        self.layout = QtWidgets.QVBoxLayout()
        self.load_button = QtWidgets.QPushButton('Load')
        self.save_button = QtWidgets.QPushButton('Save')
        self.init_UI()

    @staticmethod
    def Qapp() -> QtWidgets.QApplication:
        return QtWidgets.QApplication([])

    def init_UI(self):
        self.load_button.clicked.connect(self.load)
        self.save_button.setEnabled(self.is_image)
        self.save_button.clicked.connect(self.save)

        but_box = QtWidgets.QHBoxLayout()
        but_box.addStretch(1)

        but_box.addWidget(self.load_button, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        but_box.addWidget(self.save_button, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(self.layout)
        vbox.addLayout(but_box)

        self.setLayout(vbox)

        self.show()
        self.set_Pixmap()

    def set_Pixmap(self, ):
        pix = QtGui.QPixmap(self.Qimage)
        self.label.setPixmap(pix)
        self.label.setMargin(10)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.save_button.setEnabled(self.is_image)
        self.layout.addWidget(self.label)

    @QtCore.Slot()
    def load(self):  # Comment faire si le gars quitte la fenetre, pour arreter la fonction sans break
        image_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', os.getcwd(), 'Images (*.ulbmp *.ULBMP)')[0]
        try:
            self.image = Decoder.load_from(image_path)
        except Exception as e:
            QtWidgets.QErrorMessage(self).showMessage(str(e))

        self.set_Qimage(self.image)
        self.set_Pixmap()

    def set_Qimage(self, image: 'Image'):
        self.Qimage = QtGui.QImage(image.width, image.height, QtGui.QImage.Format_RGB32)
        for i in range(image.width):
            for j in range(image.height):
                r, g, b = image[i, j].color

                value = QtGui.qRgb(r, g, b)
                self.Qimage.setPixel(i, j, value)
        self.is_image = True

    @QtCore.Slot()
    def save(self):
        version = QtWidgets.QInputDialog.getInt(self, 'Version', 'Enter the version of the file', 1, 1, 2)[0]
        choice = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', os.getcwd(), 'Images (*.ulbmp *.ULBMP)')[0]

        if choice:
            Encoder(self.image, version).save_to(choice + '.ulbmp')


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()
    sys.exit(app.exec())
