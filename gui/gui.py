from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidgetItem
from design import Ui_MainWindow
import sys
import pandas as pd

users_data = pd.read_csv('users.csv', delimiter=',')
users = pd.DataFrame(users_data)


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.birthdayEdit.setMaximumDate(QtCore.QDate.currentDate())
        self.ui.birthdayEdit.editingFinished.connect(self.updateAge)

        self.updateTable()

        self.ui.newUserButton.clicked.connect(self.addNewUser)
        self.ui.deleteUserButton.clicked.connect(self.deleteUser)
        self.ui.exitButton.clicked.connect(self.exit)
        self.ui.table.cellClicked.connect(self.chooseUser)

        self.user = 0

    def updateAge(self):
        birthday = self.ui.birthdayEdit.date()
        now = QtCore.QDate.currentDate()

        age = now.year() - birthday.year()
        if now.month() < birthday.month():
            age -= 1
        elif now.month() == birthday.month() and now.day() < birthday.day():
            age -= 1

        self.ui.ageNumberLable.setText(str(age))

    def addNewUser(self):
        global users
        rows = self.ui.table.rowCount()

        user = [
            [str(rows), 'Name' + str(rows), 'Second' + str(rows), 'Middle' + str(rows)]
        ]
        user = pd.DataFrame(user, columns=['id', 'name', 'secondName', 'middleName'])
        users = pd.concat([users, user], ignore_index=True)

        self.updateTable()

    def deleteUser(self):
        global users

        row = self.ui.table.currentRow()
        users.drop(index=[row], axis=0, inplace=True)
        users = users.reset_index(drop=True)

        self.updateTable()
        self.ui.table.selectionModel().clearCurrentIndex()

    def chooseUser(self):
        row = self.ui.table.currentRow()
        self.user = row
        self.updateCard()

    def updateCard(self):
        user = users.iloc[self.user]
        self.ui.nameEdit.setText(user['name'])
        self.ui.secondNameEdit.setText(user['secondName'])
        self.ui.middleNameEdit.setText(user['middleName'])

    def updateTable(self):
        self.ui.table.clear()

        if len(users) > 0:
            self.ui.table.setRowCount(len(users))
            for i in range(len(users)):
                user = users.iloc[i]
                name = ' '.join([user['secondName'], user['name'], user['middleName']])
                name = QTableWidgetItem(name)
                name.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )
                self.ui.table.setItem(i, 1, name)

    def exit(self):
        users.to_csv('users.csv', index=False)
        self.close()

    def closeEvent(self, event):
        self.exit()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    application = Window()
    application.show()

    sys.exit(app.exec())
