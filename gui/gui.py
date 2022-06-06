from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidgetItem
from design import Ui_MainWindow
import sys


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.birthdayEdit.setMaximumDate(QtCore.QDate.currentDate())
        self.ui.birthdayEdit.editingFinished.connect(self.updateAge)

        self.ui.table.setRowCount(1)
        self.ui.table.setItem(0, 1, QTableWidgetItem(str("Name")))

        self.ui.newUserButton.clicked.connect(self.addNewUser)

    def updateAge(self):
        birthday = self.ui.birthdayEdit.date()
        now = QtCore.QDate.currentDate()

        age = now.year() - birthday.year()
        if now.month() > birthday.month():
            age -= 1
        elif now.month() == birthday.month() and now.day() > birthday.day():
            age -= 1

        self.ui.ageNumberLable.setText(str(age))

    def addNewUser(self):
        rows = self.ui.table.rowCount()
        self.ui.table.setRowCount(rows + 1)

        name = QTableWidgetItem("ФИО " + str(rows))
        name.setFlags(
            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        )

        self.ui.table.setItem(rows, 1, name)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    application = Window()
    application.show()

    sys.exit(app.exec())
