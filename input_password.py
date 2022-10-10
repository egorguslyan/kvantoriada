from PyQt5 import QtWidgets
from input_password_design import Ui_Dialog


class CheckPassword(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, user):
        super(CheckPassword, self).__init__()
        self.setupUi(self)
        self.setModal(True)

        self.user = user
        self.check = False

        self.passwordWarning.setVisible(False)

        self.okButton.clicked.connect(self.checkPassword)

    def checkPassword(self):
        if self.user['password'] != self.passwordEdit.text():
            self.passwordWarning.setVisible(True)
        else:
            self.passwordWarning.setVisible(False)
            self.check = True

            self.close()
