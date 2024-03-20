"""
NOM : <Kazberuk>
PRÉNOM : <Denis>
SECTION : <INFO>
MATRICULE : <000589811>
"""

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
        popup = PopupWindow()
        popup.exec()
        rle, version, depth = popup.get_values()
        # if rle and depth < 8:
        #     # Normally it's useless. But somehow there is a bug with the popup window
        #     QtWidgets.QErrorMessage(self).showMessage('La profondeur doit être supérieure ou égale à 8 pour le RLE')
        #     return

        choice = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', os.getcwd(), 'Images (*.ulbmp *.ULBMP)')[0]

        if choice:
            extension = '.ulbmp' if not choice.endswith('.ulbmp') else ''
            Encoder(self.image, version, rle=rle, depth=depth).save_to(choice + extension)


class PopupWindow(QtWidgets.QDialog, QtWidgets.QWidget):
    """
    Class for the popup window, to choose the version and depth of the image
    """
    def __init__(self):
        super().__init__()
        # ComboBox for version
        self.__enable_rle = False
        self.__enable_version = False
        self.checkbox = QtWidgets.QCheckBox("Compression RLE")
        self.checkbox.setEnabled(self.enable_rle)
        self.combobox_version_name = QtWidgets.QLabel("Version")
        self.combobox_version = QtWidgets.QComboBox()
        self.combobox_version.addItems(["1", "2", "3", "4"])
        self.combobox_version.currentTextChanged.connect(self.combo_version_changed)

        # ComboBox for depth
        self.combobox_depth_name = QtWidgets.QLabel("Profondeur")
        self.combobox_depth = QtWidgets.QComboBox()
        self.combobox_depth.addItems(["1", "2", "4", "8", "24"])
        self.combobox_depth.setEnabled(self.enable_version)
        self.combobox_depth.currentTextChanged.connect(self.combo_depth_changed)

        self.button_ok = QtWidgets.QPushButton("OK")
        self.button_cancel = QtWidgets.QPushButton("Annuler")

        self.add_layout()

        self.button_ok.clicked.connect(self.accept)
        self.button_cancel.clicked.connect(self.reject)

    @property
    def enable_rle(self):
        return self.__enable_rle

    @enable_rle.setter
    def enable_rle(self, value: bool):
        self.__enable_rle = value

    @property
    def enable_version(self):
        return self.__enable_version

    @enable_version.setter
    def enable_version(self, value: bool):
        self.__enable_version = value

    def add_layout(self):
        layout = QtWidgets.QVBoxLayout()
        layout_ask = QtWidgets.QVBoxLayout()
        layout_ask.addWidget(self.checkbox)

        layout_combo_version = QtWidgets.QHBoxLayout()
        layout_combo_version.addWidget(self.combobox_version_name)
        layout_combo_version.addWidget(self.combobox_version)

        layout_combo_depth = QtWidgets.QHBoxLayout()
        layout_combo_depth.addWidget(self.combobox_depth_name)
        layout_combo_depth.addWidget(self.combobox_depth)

        layout_ask.addLayout(layout_combo_version)
        layout_ask.addLayout(layout_combo_depth)

        layout_valid = QtWidgets.QHBoxLayout()
        layout_valid.addWidget(self.button_ok)
        layout_valid.addWidget(self.button_cancel)

        layout.addLayout(layout_ask)
        layout.addLayout(layout_valid)

        self.setLayout(layout)

    def get_values(self):
        rle = self.checkbox.isChecked()
        try:
            version = int(self.combobox_version.currentText()) if self.combobox_version.currentText().isdigit() else None
            depth = int(self.combobox_depth.currentText()) if self.combobox_depth.currentText().isdigit() else None
        except Exception as e:
            raise Exception(e)
        return rle, version, depth

    def combo_version_changed(self, text: str):
        if text == "2":
            self.enable_rle = True
            self.checkbox.setEnabled(self.enable_rle)
        elif text == "4":
            self.enable_version = True
            self.combobox_depth.setEnabled(self.enable_version)
        else:
            self.enable_rle = False
            self.enable_version = False
            self.checkbox.setEnabled(self.enable_rle)
            self.combobox_depth.setEnabled(self.enable_version)

    def combo_depth_changed(self, text: str):
        if text == "8":
            self.enable_rle = True
            self.checkbox.setEnabled(self.enable_rle)
        elif text == "24":
            self.enable_rle = True
            self.checkbox.setEnabled(self.enable_rle)
        else:
            self.enable_rle = False
            self.checkbox.setEnabled(self.enable_rle)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()
    sys.exit(app.exec())