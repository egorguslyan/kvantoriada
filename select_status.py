from PyQt5 import QtWidgets
# from PyQt5 import QtCore, QtGui
from select_status_design import Ui_Form


class SelectStatus(QtWidgets.QWidget, Ui_Form):
    def __init__(self, *args, **kwargs):
        super(SelectStatus, self).__init__(*args, **kwargs)
        self.setupUi(self)

    def getStatus(self):
        """
        Получить выбранное состояние
        :return: int
        """
        up = self.upButton.isChecked()
        normal = self.normalButton.isChecked()
        down = self.downButton.isChecked()

        if down:
            return 1
        elif normal:
            return 2
        elif up:
            return 3
        else:
            return 0
