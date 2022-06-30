from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidgetItem
from design import Ui_MainWindow
import sys
import pandas as pd
import os
import shutil
import time
import datetime

from mplcanvas import MplCanvas

from bluetooth_serial.read_serial import read
from analysis.ecg_analysis import analysis_ecg
from analysis.eeg_analysis import analysis_eeg
from analysis.signal_analysis import open_csv_file
from analysis.prediction import prediction

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
        self.ui.updateUserButton.clicked.connect(self.updateUser)
        self.ui.testButton.clicked.connect(self.testUser)
        self.ui.repeatButton.clicked.connect(self.testUser)

        self.ui.ecgFilesCombo.activated[str].connect(self.selectFile)
        self.ui.eegFilesCombo.activated[str].connect(self.selectFile)

        self.ui.canvasECG = MplCanvas()
        self.ui.verticalLayout_8.addWidget(self.ui.canvasECG)

        self.ui.canvasEEG = MplCanvas()
        self.ui.verticalLayout_7.addWidget(self.ui.canvasEEG)

        self.ui.canvasVar = MplCanvas()
        self.ui.verticalLayout_10.addWidget(self.ui.canvasVar)

        self.ui.saveButton = QtWidgets.QPushButton(self.ui.centralwidget)
        self.ui.saveButton.setStyleSheet("background-color: #e1a91a;")
        self.ui.saveButton.setObjectName("saveButton")
        self.ui.saveButton.setText('Сохранить')
        self.ui.saveButton.setVisible(False)
        self.ui.saveButton.clicked.connect(self.saveChanges)
        self.ui.horizontalLayout_9.insertWidget(2, self.ui.saveButton)

        if not users.empty:
            self.user = 0
            self.updateCard()
        else:
            self.user = None

        self.file_path = None

    def updateAge(self):
        birthday = self.ui.birthdayEdit.date()
        now = QtCore.QDate.currentDate()

        age = now.year() - birthday.year()
        if now.month() < birthday.month():
            age -= 1
        elif now.month() == birthday.month() and now.day() < birthday.day():
            age -= 1

        self.ui.ageNumberLabel.setText(str(age))

    def addNewUser(self):
        global users
        rows = self.ui.table.rowCount()
        date = QtCore.QDate.currentDate().toString('dd.MM.yyyy')

        dir_path = os.path.join('users', str(int(time.time())))
        os.mkdir(dir_path)

        user = [
            ['Name' + str(rows), 'Second' + str(rows), 'Middle' + str(rows), date, dir_path, 'None', '']
        ]
        user = pd.DataFrame(user, columns=[
            'name',
            'secondName',
            'middleName',
            'birthday',
            'dir_path',
            'password',
            'last_result'
        ])
        users = pd.concat([users, user], ignore_index=True)

        self.updateTable()

    def deleteUser(self):
        global users

        row = self.ui.table.currentRow()
        if row > -1:
            user = users.iloc[self.user]
            shutil.rmtree(user['dir_path'])

            users.drop(index=[row], axis=0, inplace=True)
            users = users.reset_index(drop=True)

            if len(users) > 0:
                self.user = 0
                self.updateCard()
            else:
                self.user = None

            self.updateTable()
            self.ui.table.selectionModel().clearCurrentIndex()

    def chooseUser(self):
        row = self.ui.table.currentRow()
        self.user = row
        self.updateCard()

    def updateCard(self):
        if self.user is not None:
            user = users.iloc[self.user]
            self.ui.nameEdit.setText(user['name'])
            self.ui.secondNameEdit.setText(user['secondName'])
            self.ui.middleNameEdit.setText(user['middleName'])
            date = QtCore.QDate.fromString(user['birthday'], 'dd.MM.yyyy')
            self.ui.birthdayEdit.setDate(date)
            self.ui.birthdayEdit.show()
            self.updateAge()
            self.ui.ecgFilesCombo.clear()
            files = os.listdir(user['dir_path'])
            if len(files) > 0:
                for file in files:
                    if file.find('r_') == -1:
                        self.ui.ecgFilesCombo.addItem(file)
                        self.ui.eegFilesCombo.addItem(file)

            self.ui.btnPassword.clicked.connect(self.editingResult)
            self.ui.btnPassword.clicked.disconnect()

            if user['password'] != 'None':
                self.ui.btnPassword.clicked.connect(self.editingResult)
                self.ui.btnPassword.setText('Войти')
            else:
                self.ui.btnPassword.clicked.connect(self.createPassword)
                self.ui.btnPassword.setText('Создать')

        self.ui.canvasECG.clear()
        self.ui.canvasEEG.clear()
        self.ui.canvasVar.clear()

        self.changeEditingLabel(False)
        self.clearLabels()
        self.file_path = None
        self.ui.saveButton.setVisible(False)
        self.ui.password.setStyleSheet("QLineEdit { background-color : #ffffff }")

        self.ui.tab.setStyleSheet("background-color: rgb(255, 230, 234);\n"
                                  "alternate-background-color: rgb(170, 85, 255);")

    def clearLabels(self):
        self.ui.heartRateLabel.clear()
        self.ui.breathFreqLabel.clear()
        self.ui.breathAmplitudeLabel.clear()
        self.ui.variabilityIndexLabel.clear()
        self.ui.variabilityAmplitudeLabel.clear()

        self.ui.amplitudeAlphaLabel.clear()
        self.ui.startTimeAlphaLabel.clear()

        self.ui.resultTextLabel.clear()

    def updateTable(self):
        self.ui.table.clear()
        # self.ui.table.setHorizontalHeaderLabels(['', 'Спортсмен'])

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

                result = QTableWidgetItem(user['last_result'])
                result.setFlags(
                    QtCore.Qt.ItemIsEnabled
                )
                self.ui.table.setItem(i, 0, result)

    def updateUser(self):
        global users

        if self.ui.updateUserButton.text() == 'Изменить':
            self.ui.secondNameEdit.setReadOnly(False)
            self.ui.nameEdit.setReadOnly(False)
            self.ui.middleNameEdit.setReadOnly(False)
            self.ui.birthdayEdit.setReadOnly(False)
            self.ui.newUserButton.setEnabled(False)
            self.ui.deleteUserButton.setEnabled(False)
            self.ui.testButton.setEnabled(False)
            self.ui.table.setEnabled(False)

            self.ui.updateUserButton.setText('Сохранить')
        else:
            self.ui.secondNameEdit.setReadOnly(True)
            self.ui.nameEdit.setReadOnly(True)
            self.ui.middleNameEdit.setReadOnly(True)
            self.ui.birthdayEdit.setReadOnly(True)
            self.ui.newUserButton.setEnabled(True)
            self.ui.deleteUserButton.setEnabled(True)
            self.ui.testButton.setEnabled(True)
            self.ui.table.setEnabled(True)

            self.ui.updateUserButton.setText('Изменить')

            user = [
                self.ui.nameEdit.text(),
                self.ui.secondNameEdit.text(),
                self.ui.middleNameEdit.text(),
                self.ui.birthdayEdit.dateTime().toString('dd.MM.yyyy'),
                users.iloc[self.user]['dir_path']
            ]
            users.at[self.user] = user
            self.updateTable()

    def testUser(self):
        user = users.iloc[self.user]
        dir_path = user['dir_path']
        date = datetime.datetime.now().strftime('%d.%m.%Y %H-%M-%S')
        file_path = os.path.join(dir_path, f"{date}.csv")

        self.ui.testDateLabel.setText(date)
        self.ui.resultTextLabel.setText("тестируется")

        self.ui.ecgFilesCombo.addItem(date)
        self.ui.eegFilesCombo.addItem(date)

        if read('COM6', file_path):
            self.analysis(file_path)
        else:
            self.ui.resultTextLabel.setText("не удалось подключиться")

    def selectFile(self, text):
        dir_path = users.iloc[self.user]['dir_path']
        file_path = os.path.join(dir_path, text)
        self.analysis(file_path)

    def analysis(self, file_path):
        self.file_path = file_path

        ecg = self.updateECG(file_path)
        eeg = self.updateEEG(file_path)

        status = prediction(ecg, eeg)
        self.ui.resultTextLabel.setText(status['result']['text'])
        self.ui.resultTextLabel.setColor(status['result']['color'])

        self.ui.heartRateLabel.setColor(status['heart_rate'])
        self.ui.breathFreqLabel.setColor(status['breath']['freq'])
        self.ui.variabilityIndexLabel.setColor(status['variability']['index'])
        
        self.ui.startTimeAlphaLabel.setColor(status['spectrum']['start_time'])

        result = QTableWidgetItem(status['result']['text'])
        result.setFlags(
            QtCore.Qt.ItemIsEnabled
        )
        self.ui.table.setItem(self.user, 0, result)

        user = users.iloc[self.user]
        user['last_result'] = status['result']['text']
        users.at[self.user] = user

        self.makeResultFile(file_path)

    def makeResultFile(self, file_path):
        result = [
            ['heart_rate', self.ui.heartRateLabel.color, self.ui.heartRateLabel.text()],
            ['breath_freq', self.ui.breathFreqLabel.color, self.ui.breathFreqLabel.text()],
            ['variability_index', self.ui.variabilityIndexLabel.color, self.ui.variabilityIndexLabel.text()],
            ['start_time', self.ui.startTimeAlphaLabel.color, self.ui.startTimeAlphaLabel.text()],
            ['result', self.ui.resultTextLabel.color, '']
        ]
        result_table = pd.DataFrame(result, columns=['ind', 'result', 'value'])
        filename, file_extension = os.path.splitext(file_path)
        # print(filename + '_r' + file_extension)
        result_table.to_csv(filename + '_r' + file_extension, index=False)

    def updateECG(self, file_path):
        data = open_csv_file(file_path)
        properties = analysis_ecg(data['ecg'])

        self.ui.canvasECG.clear()
        self.ui.canvasECG.plot(properties['time'], data['ecg'])
        self.ui.canvasECG.save_data()
        self.ui.canvasECG.set_ylim()

        self.ui.canvasVar.clear()
        self.ui.canvasVar.plot(range(0, 2000, 50), properties['variability']['histogram'])
        self.ui.canvasVar.save_data()
        self.ui.canvasVar.set_ylim()

        self.ui.heartRateLabel.setText(str(properties['heart_rate']))
        self.ui.variabilityAmplitudeLabel.setText(str(properties['variability']['amplitude']))
        self.ui.variabilityIndexLabel.setText(str(properties['variability']['index']))
        self.ui.breathAmplitudeLabel.setText(str(properties['breath']['amplitude']))
        self.ui.breathFreqLabel.setText(str(properties['breath']['freq']))

        return properties

    def updateEEG(self, file_path):
        data = open_csv_file(file_path)
        properties = analysis_eeg(data['eeg'])

        self.ui.canvasEEG.clear()
        self.ui.canvasEEG.plot(properties['time'], properties['filtered'])
        self.ui.canvasEEG.save_data()
        self.ui.canvasEEG.set_ylim()

        self.ui.amplitudeAlphaLabel.setText(str(properties['spectrum']['amp']))
        self.ui.startTimeAlphaLabel.setText(str(properties['spectrum']['start_time']))

        return properties

    def changeEditingLabel(self, flag):
        self.ui.heartRateLabel.setEditable(flag)
        self.ui.variabilityAmplitudeLabel.setEditable(flag)
        self.ui.variabilityIndexLabel.setEditable(flag)
        self.ui.breathFreqLabel.setEditable(flag)
        self.ui.breathAmplitudeLabel.setEditable(flag)

        self.ui.startTimeAlphaLabel.setEditable(flag)
        self.ui.amplitudeAlphaLabel.setEditable(flag)

        self.ui.resultTextLabel.setEditable(flag)

    def editingMode(self):
        self.ui.tab.setStyleSheet("background-color: rgb(255, 196, 197);\n"
                                  "alternate-background-color: rgb(170, 85, 255);")
        self.changeEditingLabel(True)
        self.ui.saveButton.setVisible(True)

    def saveChanges(self):
        print('save')
        self.makeResultFile(self.file_path)

    def editingResult(self):
        user = users.iloc[self.user]

        if self.ui.password.text() == user['password'] and self.file_path is not None:
            self.editingMode()
            self.ui.password.setStyleSheet("QLineEdit { background-color : #ffffff }")
        else:
            self.ui.password.setStyleSheet("QLineEdit { background-color : #c73636 }")

        self.ui.password.setText('')

    def createPassword(self):
        user = users.iloc[self.user]
        if user['password'] == 'None':
            if self.ui.password.text() != '':
                user['password'] = self.ui.password.text()
                users.at[self.user] = user
                self.ui.btnPassword.setText('Подтвердить')
            else:
                self.ui.password.setStyleSheet("QLineEdit { background-color : #c73636 }")
        else:
            if user['password'] == self.ui.password.text():
                self.ui.btnPassword.clicked.disconnect()
                self.ui.btnPassword.clicked.connect(self.editingResult)
                self.ui.password.setStyleSheet("QLineEdit { background-color : #ffffff }")
                self.ui.btnPassword.setText('Войти')
            else:
                self.ui.password.setStyleSheet("QLineEdit { background-color : #c73636 }")

        self.ui.password.setText('')

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
