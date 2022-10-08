from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5 import QtCore
from list_account_design import Ui_Dialog
# import sys
import pandas as pd


class ListAccount(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, mode, users):
        super().__init__()
        self.setupUi(self)
        self.setModal(True)
        self.mode = mode
        self.users = users

        self.updateTable()  # обновление таблицы пользователей

        # если есть пользователи, то загрузить карточку первого пользователя
        if not self.users.empty:
            self.user = 0
            self.updateCard()
        else:
            self.user = None

    def updateTable(self):
        """
        Обновление таблицы аккаунтов
        :return: None
        """
        self.tableWidget.clear()
        # self.ui.table.setHorizontalHeaderLabels(['', 'Спортсмен'])

        if len(self.users) > 0:
            self.tableWidget.setRowCount(len(self.users))
            for i in range(len(self.users)):
                user = self.users.iloc[i]
                name = QTableWidgetItem(user[self.mode + '_name'])
                name.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )
                self.tableWidget.setItem(i, 0, name)

    def updateCard(self):
        """
        Обновление карточки пользователя
        :return: None
        """
        self.ui.tab.setCurrentIndex(0)

        # если выбран пользователь, загрузить его данные
        if self.user is not None:
            user = self.users.iloc[self.user]
            a = user[self.mode + '_name']
            name, surname, middlename = '', '', ''

            if len(a) >= 1:
                name = a[0]
            if len(a) >= 2:
                name = a[1]
            if len(a) >= 3:
                middlename = a[2]
            self.nameEdit.setText(name)
            self.surnameEdit.setText(surname)
            self.middleNameEdit.setText(middlename)

            # ДОБАВИТЬ ОБНОВЛЕНИЕ СПИСКА СПОРТСМЕНОВ
