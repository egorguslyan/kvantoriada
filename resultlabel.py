from PyQt5 import QtWidgets, QtCore


class ResultLabel(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.color = 1
        self.setStyleSheet("QLabel { background-color : white; }")
        self.__colors = ['#5555ff', '#89ad3b', '#c73636', '#ffffff']
        self._results = {
            'normal': 1,
            'relaxed': 0,
            'excited': 2,
            'clear': 3
        }

        self.__cnt = 0

        self.isEditable = False

    def mouseDoubleClickEvent(self, event):
        print(event.button())

    def wheelEvent(self, event):
        if self.isEditable:
            if self.__cnt < 2:
                self.__cnt += 1
                return
            self.__cnt = 0
            if event.angleDelta().y() == 120:
                self.color += 1
            else:
                self.color -= 1

            self.color %= 3
            self.setColor(self.color)

    def setEditable(self, mode):
        self.isEditable = mode

    def setColor(self, result):
        if isinstance(result, str):
            self.color = self._results[result]
        elif isinstance(result, int) or isinstance(result, float):
            self.color = int(result)
        self.set_background_color()

    def set_background_color(self):
        self.setStyleSheet("QLabel { background-color : " + self.__colors[self.color] + "; }")

    def clear(self):
        self.setText('')
        self.setColor('clear')


class Result(ResultLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setColor(self, result):
        if isinstance(result, str):
            self.color = self._results[result]
        elif isinstance(result, int) or isinstance(result, float):
            self.color = int(result)
        self.set_background_color()
        results = {
            1: "Норма",
            0: "Подавлен",
            2: "Возбужден",
            3: ""
        }
        self.setText(results[self.color])
