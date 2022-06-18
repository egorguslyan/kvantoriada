from PyQt5 import QtWidgets, QtCore


class ResultLabel(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.color = 1
        self.setStyleSheet("QLabel { background-color : white; }")
        self.colors__ = ['blue', 'green', 'red']

    def mouseDoubleClickEvent(self, event):
        print(event.button())

    def wheelEvent(self, event):
        print(event.angleDelta().y())
        if event.angleDelta().y() == 120:
            self.color += 1
        else:
            self.color -= 1

        self.color %= 3
        self.set_background_color()

    def set_background_color(self):
        self.setStyleSheet("QLabel { background-color : " + self.colors__[self.color] + "; }")
