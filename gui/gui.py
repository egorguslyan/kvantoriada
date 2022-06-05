from PyQt5 import QtWidgets
from design import Ui_MainWindow
import sys


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


app = QtWidgets.QApplication([])
application = Window()
application.show()

sys.exit(app.exec())
