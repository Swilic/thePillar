"""
NOM : <Kazberuk>
PRÉNOM : <Denis>
SECTION : <INFO>
MATRICULE : <000589811>
"""

from PySide6 import QtWidgets


class PopupWindow(QtWidgets.QDialog, QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # ComboBox for version
        self.checkbox = QtWidgets.QCheckBox("Compression RLE")
        self.combobox_version_name = QtWidgets.QLabel("Version")
        self.combobox_version = QtWidgets.QComboBox()
        self.combobox_version.addItems(["1", "2", "3", "4"])

        # ComboBox for depth
        self.combobox_depth_name = QtWidgets.QLabel("Profondeur")
        self.combobox_depth = QtWidgets.QComboBox()
        self.combobox_depth.addItems(["1", "2", "4", "8", "24"])

        self.button_ok = QtWidgets.QPushButton("OK")
        self.button_cancel = QtWidgets.QPushButton("Annuler")

        self.add_layout()

        self.button_ok.clicked.connect(self.accept)
        self.button_cancel.clicked.connect(self.reject)

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


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = PopupWindow()
