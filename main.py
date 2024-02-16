from window import MyWidget

if __name__ == "__main__":
    app = MyWidget.Qapp()
    widget = MyWidget()
    widget.show()
    app.exec()
