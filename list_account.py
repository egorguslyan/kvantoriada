from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidgetItem, QStyledItemDelegate
from PyQt5.QtGui import QColor, QPalette
from list_account_design import Ui_Dialog
from input_password import CheckPassword
# import sys
import pandas as pd


class ColorDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.data() == 'Боевая готовность':
            option.palette.setColor(QPalette.Text, QColor("green"))
        elif index.data() == 'Предстартовая апатия':
            option.palette.setColor(QPalette.Text, QColor("blue"))
        elif index.data() == 'Предстартовая лихорадка':
            option.palette.setColor(QPalette.Text, QColor("red"))
        QStyledItemDelegate.paint(self, painter, option, index)


class ListAccount(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, mode, users, sportsmen, user):
        super().__init__()
        self.setupUi(self)
        self.setModal(True)
        self.mode = mode
        self.users = users
        self.sportsmen = sportsmen

        modes = {'doctor': 'врачей',
                 'couch': 'тренеров'}
        self.setWindowTitle('Редактирование списка ' + modes[mode])

        self.spacer1.setVisible(False)
        self.spacer2.setVisible(False)

        # добавление событий
        self.tableWidget.cellClicked.connect(self.chooseUser)
        self.newPasswordButton.clicked.connect(self.newPassword)
        self.savePasswordButton.clicked.connect(self.saveNewPassword)
        self.updateUserButton.clicked.connect(self.updateUser)
        self.newUserButton.clicked.connect(self.addNewUser)
        self.deleteUserButton.clicked.connect(self.deleteUser)
        self.unlinkAccountButton.clicked.connect(self.unlinkUser)

        self.updateTable()  # обновление таблицы пользователей

        # если есть пользователи, то загрузить карточку первого пользователя
        if not self.users.empty and user != -1:
            dialog = CheckPassword(self.users.iloc[user])
            dialog.show()
            dialog.exec()
            if dialog.check:
                self.user = user
            else:
                self.user = None
        else:
            self.user = None

        self.updateCard()

    def chooseUser(self):
        """
        Выбор пользователя
        :return: None
        """
        row = self.tableWidget.currentRow()
        # Если пользователь изменился, проверить его пароль
        if row != self.user:
            dialog = CheckPassword(self.users.iloc[row])
            dialog.show()
            dialog.exec()
            if dialog.check:
                self.user = row
                self.updateCard()

    def updateTable(self):
        """
        Обновление таблицы аккаунтов
        :return: None
        """
        self.tableWidget.clear()

        if len(self.users) > 0:
            self.tableWidget.setRowCount(len(self.users))
            for i in range(len(self.users)):
                user = self.users.iloc[i]
                name = QTableWidgetItem(user['name'])
                name.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )
                self.tableWidget.setItem(i, 0, name)

    def updateCard(self):
        """
        Обновление карточки пользователя
        :return: None
        """
        # сброс всех настроек
        self.tabWidget.setCurrentIndex(0)
        self.passwordWarning.setVisible(False)
        self.newPasswordMode(False)
        self.nameEdit.setText('')
        self.surnameEdit.setText('')
        self.middleNameEdit.setText('')

        # если выбран пользователь, загрузить его данные
        if self.user is not None:
            user = self.users.iloc[self.user]
            a = user['name'].split()
            name, surname, middlename = '', '', ''

            if len(a) >= 1:
                surname = a[0]
            if len(a) >= 2:
                name = a[1]
            if len(a) >= 3:
                middlename = a[2]
            self.nameEdit.setText(name)
            self.surnameEdit.setText(surname)
            self.middleNameEdit.setText(middlename)

            self.updateSportsmenTable(user['name'])  # Обновление списка спортсменов
        else:
            self.updateSportsmenTable('')

    def updateSportsmenTable(self, username):
        """
        Обновление списка спортсменов
        :param username: string
        :return: None
        """
        self.sportsmenTable.clear()  # Очищение таблицы
        self.sportsmenTable.setItemDelegateForColumn(1, ColorDelegate())
        # Получение списка спортсменов, находящихся под руководством пользователя
        sportsmen = self.sportsmen[self.sportsmen[self.mode + '_name'] == username]
        self.sportsmenTable.setRowCount(len(sportsmen))

        # Задавание горизонтального заголовка
        self.sportsmenTable.setHorizontalHeaderLabels(['Спортсмен', 'Результат тестирования'])
        # Отображение спортсменов в таблице
        for i in range(len(sportsmen)):
            sportsman = sportsmen.iloc[i]
            # print(i, sportsman)
            full_name = ' '.join([sportsman['surname'], sportsman['name'], sportsman['middleName']])
            name = QTableWidgetItem(full_name)
            self.sportsmenTable.setItem(i, 0, name)
            if sportsman['last_result'] == 'normal':
                result = 'Боевая готовность'
            elif sportsman['last_result'] == 'depressed':
                result = 'Предстартовая апатия'
            elif sportsman['last_result'] == 'excited':
                result = 'Предстартовая лихорадка'
            else:
                result = ''
            result = QTableWidgetItem(result)
            self.sportsmenTable.setItem(i, 1, result)
        self.sportsmenTable.resizeColumnsToContents()

    def updatingUserMode(self, flag):
        """
        Режим изменения данных пользователя
        :param flag: Bool
        :return: None
        """
        self.surnameEdit.setReadOnly(flag)
        self.nameEdit.setReadOnly(flag)
        self.middleNameEdit.setReadOnly(flag)
        self.newUserButton.setEnabled(flag)
        self.deleteUserButton.setEnabled(flag)
        self.tableWidget.setEnabled(flag)

    def addNewUser(self):
        """
        Создание нового пользователя
        :return: None
        """
        rows = self.tableWidget.rowCount()

        user = {
            'name': 'Name' + str(rows),
            'password': '12345678',
            'linked_account': 'None'
        }
        user = pd.DataFrame([list(user.values())], columns=list(user.keys()))
        self.users = pd.concat([self.users, user], ignore_index=True)

        self.updateTable()

        self.saveTable()

    def deleteUser(self):
        """
        Удаление выбранного пользователя и всех его данных
        :return: None
        """
        # Если выбран пользователь, то удалить его
        if self.user is not None:
            user = self.users.iloc[self.user]
            self.updateSportsmen(user['name'])
            self.users.drop(index=[self.user], axis=0, inplace=True)
            self.users.reset_index(drop=True, inplace=True)

            self.user = None
            self.updateCard()

            self.updateTable()
            self.tableWidget.selectionModel().clearCurrentIndex()

            self.saveTable()

    def updateSportsmen(self, username):
        """
        При удалении пользователя, удалить его упоминание в таблице спортсменов
        :param username: string
        :return: None
        """
        self.sportsmen.loc[self.sportsmen[self.mode + '_name'] == username, self.mode + '_name'] = 'None'

    def updateUser(self):
        """
        Изменение данных пользователя
        :return: None
        """
        # Если выбран пользователь
        if self.user is not None:
            if self.updateUserButton.text() == 'Изменить':
                self.updatingUserMode(False)
                self.updateUserButton.setText('Сохранить')
            else:
                name, surname, middlename = '', '', ''
                if self.surnameEdit.text() != '':
                    surname = self.surnameEdit.text()
                    self.surnameEdit.setStyleSheet('QLineEdit { background-color : #ffffff; }')
                else:
                    self.surnameEdit.setStyleSheet('QLineEdit { background-color : #c73636; }')

                if self.nameEdit.text() != '':
                    name = self.nameEdit.text()
                    self.nameEdit.setStyleSheet('QLineEdit { background-color : #ffffff; }')
                else:
                    self.nameEdit.setStyleSheet('QLineEdit { background-color : #c73636; }')

                if self.middleNameEdit.text() != '':
                    middlename = self.middleNameEdit.text()
                    self.middleNameEdit.setStyleSheet('QLineEdit { background-color : #ffffff; }')

                if name == '' or surname == '':
                    return

                last_name = self.users.at[self.user, 'name']
                full_name = ' '.join([surname, name, middlename])
                self.users.at[self.user, 'name'] = full_name
                self.sportsmen.loc[(self.sportsmen[self.mode + '_name'] == last_name), self.mode + '_name'] = full_name
                self.updateTable()

                self.updatingUserMode(True)
                self.updateUserButton.setText('Изменить')

                self.saveTable()

    def unlinkUser(self):
        """
        Отвязать аккаунт в телеграмме
        :return: None
        """
        if self.user is not None:
            self.users.at[self.user, 'linked_account'] = 'None'
            self.saveTable()

    def newPasswordMode(self, flag):
        """
        Режим создания нового пароля
        :param flag: Bool
        :return: None
        """
        self.newPasswordButton.setVisible(not flag)
        self.passwordEdit.setVisible(flag)
        self.repeatPasswordEdit.setVisible(flag)
        self.passwordLabel.setVisible(flag)
        self.repeatPasswordLabel.setVisible(flag)
        self.savePasswordButton.setVisible(flag)

    def checkPassword(self):
        """
        Проверка пароля на корректность
        :return: bool
        """
        return self.passwordEdit.text() == self.repeatPasswordEdit.text() and self.passwordEdit.text() != ''

    def saveNewPassword(self):
        """
        Сохранение нового пароля
        :return: None
        """
        # Если пароль корректный, то сохранить его
        if self.checkPassword():
            self.users.at[self.user, 'password'] = self.passwordEdit.text()
            self.passwordWarning.setVisible(False)
            self.passwordEdit.setText('')
            self.repeatPasswordEdit.setText('')
            self.newPasswordMode(False)

            self.saveTable()
        else:
            self.passwordWarning.setVisible(True)

    def newPassword(self):
        """
        Создать новый пароль
        :return: None
        """
        if self.user is not None:
            self.newPasswordMode(True)

    def saveTable(self):
        """
        Сохранение таблицы пользователя
        :return: None
        """
        filename = {
            'couch': 'couches.csv',
            'doctor': 'doctors.csv'
        }
        self.users.to_csv(filename[self.mode], index=False)  # сохранение таблицы пользователей

    def closeEvent(self, event):
        """
        Закрытие главного окна
        :return: None
        """
        self.close()
