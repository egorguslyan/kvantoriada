from PyQt5 import QtWidgets
# from PyQt5 import QtCore, QtGui
from create_account_design import Ui_Dialog
# import sys
import pandas as pd


class CreateAccount(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, mode):
        super(CreateAccount, self).__init__()
        self.setupUi(self)
        self.setModal(True)
        endings = {'doctor': 's',
                   'couch': 'es'}
        self.filename = f'{mode}{endings[mode]}.csv'
        self.mode = mode
        self.table = pd.read_csv(self.filename, delimiter=',', dtype='str').set_index(mode + '_name')

        modes = {'doctor': 'врача',
                 'couch': 'тренера'}

        self.setObjectName('Зарегистрировать нового ' + modes[mode])
        self.nameLabel.setText('ФИО ' + modes[mode])

        self.createButton.clicked.connect(self.addNewAccount)

        self.nameWarning.setHidden(True)
        self.passwordWarning.setHidden(True)

    def checkName(self):
        return self.table[self.mode + '_name'].isin([self.nameEdit.text()]).any()\
               and self.nameEdit.text() != ''

    def checkPassword(self):
        return self.passwordEdit.text() == self.repeatPasswordEdit.text()

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

        account = pd.DataFrame([self.nameEdit.text(), self.passwordEdit.text(), None],
                               columns=[self.mode + '_name', 'couch_password', 'linked_account'])
        self.table = pd.concat([self.table, account], ignore_index=True)

        self.table.to_csv(self.filename)

        self.close()

