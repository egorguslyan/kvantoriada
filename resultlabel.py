from PyQt5 import QtWidgets
# from PyQt5 import QtCore


class ResultLabel(QtWidgets.QLabel):
    """
    Label с возможностью редактировать фон
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.color = 1
        self.setStyleSheet("QLabel { background-color : white; }")
        self.__colors = ['#5555ff', '#89ad3b', '#c73636', '#ffffff']

        self._results = {
            'normal': 1,
            'depressed': 0,
            'excited': 2,
            'clear': 3
        }
        self._r_results = {
             1: 'normal',
             0: 'depressed',
             2: 'excited'
        }

        self.__cnt = 0

        self.isEditable = False

    def wheelEvent(self, event):
        """
        Изменение цвета при прокрутке колесика мыши
        :param event:
        :return: None
        """
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
        """
        Режим редактирования
        :param mode: Bool
        :return: None
        """
        self.isEditable = mode

    def setColor(self, result):
        """
        Изменение цвета
        :param result: string or number
        :return: None
        """
        if isinstance(result, str):
            self.color = self._results[result]
        elif isinstance(result, int) or isinstance(result, float):
            self.color = int(result)
        self.set_background_color()

    def set_background_color(self):
        """
        Изменение фона
        :return: None
        """
        self.setStyleSheet("QLabel { background-color : " + self.__colors[self.color] + "; }")

    def get_result(self):
        """
        Получение состояние в строковой форме
        :return: str
        """
        return self._r_results[self.color]

    def clear(self):
        """
        Очистка
        :return: None
        """
        self.setText('')
        self.setColor('clear')


class Result(ResultLabel):
    """
    Label с возможностью редактировать фон и текст
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setColor(self, result):
        """
        Изменение цвета и текста
        :param result: string or number
        :return: None
        """
        if isinstance(result, str):
            self.color = self._results[result]
        elif isinstance(result, int) or isinstance(result, float):
            self.color = int(result)
        self.set_background_color()

        results = {
            1: "Боевая готовность",
            0: "Предстартовая апатия",
            2: "Предстартовая лихорадка",
            3: ""
        }
        self.setText(results[self.color])
