from PyQt5 import QtWidgets
# from PyQt5 import QtCore, QtGui
from create_account_design import Ui_Dialog
# import sys
import pandas as pd


class CreateAccount(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, mode, table):
        super(CreateAccount, self).__init__()
        self.setupUi(self)
        self.setModal(True)
        self.mode = mode
        self.table = table
        self.account = None

        modes = {'doctor': 'врача',
                 'couch': 'тренера'}

        self.setObjectName('Зарегистрировать нового ' + modes[mode])
        self.nameLabel.setText('ФИО ' + modes[mode])

        self.createButton.clicked.connect(self.addNewAccount)

        self.nameWarning.setHidden(True)
        self.passwordWarning.setHidden(True)

    def checkName(self):
        return self.table['name'].isin([self.nameEdit.text().title()]).any()\
               and self.nameEdit.text() != ''

    def checkPassword(self):
        return self.passwordEdit.text() != self.repeatPasswordEdit.text()

    def addNewAccount(self):
        if self.checkName():
            self.nameWarning.setHidden(False)
            return
        else:
            self.nameWarning.setHidden(True)

        if self.checkPassword():
            self.passwordWarning.setHidden(False)
            return
        else:
            self.passwordWarning.setHidden(True)

        account = pd.DataFrame([[self.nameEdit.text().title(), self.passwordEdit.text(), 'None']],
                               columns=['name', 'password', 'linked_account'])
        self.table = pd.concat([self.table, account], ignore_index=True)

        self.close()
