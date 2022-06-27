from PyQt5 import QtWidgets, QtCore


class ResultLabel(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.color = 1
        self.setStyleSheet("QLabel { background-color : white; }")
        self.__colors = ['#5555ff', '#89ad3b', '#c73636']
        self.__results = {
            'good': 1,
            'depressed': 0,
            'excited': 2
        }

        self.__cnt = 0

        self.isEditable = False

    def mouseDoubleClickEvent(self, event):
        print(event.button())

    def wheelEvent(self, event):
        if self.isEditable:
            if self.__cnt < 5:
                self.__cnt += 1
                return
            self.__cnt = 0
            if event.angleDelta().y() == 120:
                self.color += 1
            else:
                self.color -= 1

            self.color %= 3
            self.set_background_color()

    def setEditable(self, mode):
        self.isEditable = mode

    def setColor(self, result):
        self.color = self.__results[result]

    def set_background_color(self):
        self.setStyleSheet("QLabel { background-color : " + self.__colors[self.color] + "; }")
