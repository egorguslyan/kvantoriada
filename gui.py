from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QTableWidgetItem
from design import Ui_MainWindow
from dialog import Ui_Dialog
import sys
import pandas as pd
import os
import shutil
import time
import datetime
import re

from mplcanvas import MplCanvas

from bluetooth_serial.read_serial import read, get_available_ports
from analysis.ecg_analysis import analysis_ecg
from analysis.eeg_analysis import analysis_eeg
from analysis.signal_analysis import open_csv_file
from prediction.prior import prior_analysis
from prediction.prediction import fit, predict, crate_prediction_file, load_models, save_models

users_data = pd.read_csv('users.csv', delimiter=',')
users = pd.DataFrame(users_data)


class SubDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super(SubDialog, self).__init__()
        self.setupUi(self)
        self.setModal(True)


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

        self.ui.updateComButton.clicked.connect(self.updateComports)

        self.ui.filesCombo.activated[str].connect(self.selectFile)

        self.ui.canvasECG = MplCanvas()
        self.ui.verticalLayout_8.addWidget(self.ui.canvasECG)

        self.ui.canvasEEG = MplCanvas()
        self.ui.verticalLayout_7.addWidget(self.ui.canvasEEG)

        self.ui.canvasVar = MplCanvas()
        self.ui.verticalLayout_10.addWidget(self.ui.canvasVar)

        self.ui.canvasSpectrum = MplCanvas()
        self.ui.verticalLayout_6.addWidget(self.ui.canvasSpectrum)

        self.ui.saveButton.clicked.connect(self.saveResultFile)

        self.ui.deleteFile.clicked.connect(self.deleteFile)

        self.ui.predictionStatusButton.clicked.connect(self.prediction)

        self.file_path = None
        self.updateComports()

        self.dlg = SubDialog()

        if not users.empty:
            self.user = 0
            self.updateCard()
        else:
            self.user = None

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

        user = {
            'name': 'Name' + str(rows),
            'surname': 'Surname' + str(rows),
            'middleName': 'Middle' + str(rows),
            'birthday': date,
            'dir_path': dir_path,
            'password': 'None',
            'last_result': '',
            'is_editing_result_files': 0,
            'enableECG': 1,
            'timeECG': 10,
            'enableEEG': 1,
            'timeEEG': 10,
            'enableGSR': 1
        }
        user = pd.DataFrame([list(user.values())], columns=list(user.keys()))
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
        self.saveSettings()
        row = self.ui.table.currentRow()
        self.user = row
        self.updateCard()

    def updateCard(self):
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
        self.ui.tab.setCurrentIndex(0)

        if self.user is not None:
            user = users.iloc[self.user]
            self.ui.nameEdit.setText(user['name'])
            self.ui.surnameEdit.setText(user['surname'])
            self.ui.middleNameEdit.setText(user['middleName'])
            date = QtCore.QDate.fromString(user['birthday'], 'dd.MM.yyyy')
            self.ui.birthdayEdit.setDate(date)
            self.ui.birthdayEdit.show()
            self.updateAge()
            self.ui.filesCombo.clear()
            files = os.listdir(user['dir_path'])
            i = 0
            if files:
                for file in files:
                    if not re.search(r'\d\d.\d\d.\d{4} \d\d-\d\d-\d\d_\w', file) \
                            and re.search(r'\d\d.\d\d.\d{4} \d\d-\d\d-\d\d', file):
                        filename, _ = os.path.splitext(file)
                        self.ui.filesCombo.addItem(filename)

                        color = QtGui.QColor(198, 198, 198)
                        if files.count(f'{filename}_r.csv') != 0:
                            r_file = os.path.join(user['dir_path'], f"{filename}_r.csv")
                            result = pd.read_csv(r_file, delimiter=',').set_index('ind').loc['result']['result']
                            if result == 2:
                                color = QtGui.QColor(227, 138, 138)
                            elif result == 1:
                                color = QtGui.QColor(201, 245, 142)
                            else:
                                color = QtGui.QColor(155, 151, 255)
                        self.ui.filesCombo.setItemData(i, color, QtCore.Qt.BackgroundRole)
                        i += 1
            self.ui.deleteFile.setVisible(False)
            self.ui.predictionStatusButton.setVisible(False)

            comboBox = self.ui.filesCombo
            files_combo = [comboBox.itemText(i) for i in range(comboBox.count())]
            if files_combo:
                self.selectFile(files_combo[-1])

            self.ui.btnPassword.clicked.connect(self.editingResult)
            self.ui.btnPassword.clicked.disconnect()

            if user['password'] != 'None':
                self.ui.btnPassword.clicked.connect(self.editingResult)
                self.ui.btnPassword.setText('Войти')
            else:
                self.ui.btnPassword.clicked.connect(self.createPassword)
                self.ui.btnPassword.setText('Создать')

            self.ui.checkECG.setChecked(bool(user['enableECG']))
            self.ui.timeECG.setValue(int(user['timeECG']))
            self.ui.checkEEG.setChecked(bool(user['enableEEG']))
            self.ui.timeEEG.setValue(int(user['timeEEG']))
            self.ui.checkGSR.setChecked(bool(user['enableGSR']))

    def clearLabels(self):
        self.ui.heartRateLabel.clear()
        self.ui.breathFreqLabel.clear()
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
                name = ' '.join([user['surname'], user['name'], user['middleName']])
                name = QTableWidgetItem(name)
                name.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )
                self.ui.table.setItem(i, 0, name)

    def updatingUserMode(self, flag):
        self.ui.surnameEdit.setReadOnly(flag)
        self.ui.nameEdit.setReadOnly(flag)
        self.ui.middleNameEdit.setReadOnly(flag)
        self.ui.birthdayEdit.setReadOnly(flag)
        self.ui.newUserButton.setEnabled(flag)
        self.ui.deleteUserButton.setEnabled(flag)
        self.ui.testButton.setEnabled(flag)
        self.ui.table.setEnabled(flag)
        self.ui.repeatButton.setEnabled(flag)
        self.ui.predictionStatusButton.setEnabled(flag)
        self.ui.deleteFile.setEnabled(flag)
        self.ui.btnPassword.setEnabled(flag)
        self.ui.saveButton.setEnabled(flag)

    def updateUser(self):
        if self.ui.updateUserButton.text() == 'Изменить':
            self.updatingUserMode(False)
            self.ui.updateUserButton.setText('Сохранить')
        else:
            user = users.iloc[self.user].copy()
            if self.ui.surnameEdit.text() != '':
                user['surname'] = self.ui.surnameEdit.text()
                self.ui.surnameEdit.setStyleSheet("QLineEdit { background-color : #ffffff; }")
            else:
                self.ui.surnameEdit.setStyleSheet("QLineEdit { background-color : #c73636; }")
                return

            if self.ui.nameEdit.text() != '':
                user['name'] = self.ui.nameEdit.text()
                self.ui.nameEdit.setStyleSheet("QLineEdit { background-color : #ffffff; }")
            else:
                self.ui.nameEdit.setStyleSheet("QLineEdit { background-color : #c73636; }")
                return

            if self.ui.middleNameEdit.text() != '':
                user['middleName'] = self.ui.middleNameEdit.text()
                self.ui.middleNameEdit.setStyleSheet("QLineEdit { background-color : #ffffff; }")
            else:
                self.ui.middleNameEdit.setStyleSheet("QLineEdit { background-color : #c73636; }")
                return

            user['birthday'] = self.ui.birthdayEdit.dateTime().toString('dd.MM.yyyy')

            users.at[self.user] = user
            self.updateTable()

            self.updatingUserMode(True)
            self.ui.updateUserButton.setText('Изменить')

    def testUser(self):
        time_format = '%d.%m.%Y %H-%M-%S'

        user = users.iloc[self.user]
        dir_path = user['dir_path']

        date = datetime.datetime.now().strftime(time_format)
        # files = os.listdir(user['dir_path'])
        # if files:
        #     last_file = files[-1]
        #     filename, _ = os.path.splitext(last_file)
        #     if (datetime.datetime.now() - datetime.datetime.strptime(filename, time_format)).seconds < 300:
        #         os.remove(os.path.join(dir_path, f"{filename}.csv"))
        #         print(datetime.datetime.now() - datetime.datetime.strptime(filename, time_format))

        file_path = os.path.join(dir_path, f"{date}.csv")

        self.ui.testDateLabel.setText(date)

        self.ui.filesCombo.addItem(date)

        timeECG = int(self.ui.timeECG.text())
        timeEEG = int(self.ui.timeEEG.text())
        enableECG = int(self.ui.checkECG.isChecked())
        enableEEG = int(self.ui.checkEEG.isChecked())
        enableGSR = int(self.ui.checkGSR.isChecked())

        if read(self.ui.comportsCombo.currentText(), file_path,
                timeECG=timeECG, timeEEG=timeEEG,
                enableECG=enableECG, enableEEG=enableEEG, enableGSR=enableGSR):
            self.analysis(file_path)

            users.at[self.user, 'last_result'] = self.ui.resultTextLabel.color
        else:
            self.ui.resultTextLabel.setText("не удалось подключиться")

    def selectFile(self, file):
        dir_path = users.iloc[self.user]['dir_path']
        filename = os.path.join(dir_path, file)
        self.analysis(f"{filename}.csv")

    def deleteFile(self):
        user = users.iloc[self.user]

        filename = self.ui.filesCombo.currentText()
        file = f"{filename}.csv"
        file_path = os.path.join(user["dir_path"], file)

        if os.path.exists(file_path):
            os.remove(file_path)

            r_file = f"{filename}_r.csv"
            r_file_path = os.path.join(user["dir_path"], r_file)
            if os.path.exists(r_file_path):
                os.remove(r_file_path)

            p_file = f"{filename}_p.csv"
            p_file_path = os.path.join(user["dir_path"], p_file)
            if os.path.exists(p_file_path):
                os.remove(p_file_path)

        files = [self.ui.filesCombo.itemText(i) for i in range(self.ui.filesCombo.count())]
        self.ui.filesCombo.removeItem(files.index(filename))

    def analysis(self, file_path):
        self.ui.predictionStatusButton.setVisible(True)
        self.ui.deleteFile.setVisible(True)

        self.file_path = file_path

        ecg = self.updateECG(file_path)
        eeg = self.updateEEG(file_path)

        filename, _ = os.path.splitext(file_path)
        r_file = f"{filename}_r.csv"
        p_file = f"{filename}_p.csv"
        if not os.path.exists(r_file) and not os.path.exists(p_file):
            cnt_r_files = sum(map(lambda x: x.find('_r') != -1, os.listdir(users.at[self.user, 'dir_path'])))
            if cnt_r_files < 5:
                self.dlg.show()
                self.dlg.exec()

            status = prior_analysis(ecg, eeg)
            self.ui.resultTextLabel.setColor(status['result'])

            self.ui.heartRateLabel.setColor(status['heart_rate'])
            self.ui.breathFreqLabel.setColor(status['breath']['freq'])
            self.ui.variabilityIndexLabel.setColor(status['variability']['index'])

            self.ui.startTimeAlphaLabel.setColor(status['spectrum']['start_time'])
        else:
            if os.path.exists(r_file):
                status = pd.read_csv(r_file, delimiter=',')
            else:
                status = pd.read_csv(p_file, delimiter=',')
            status = status.set_index('ind')
            # print(status)
            # print(status.loc['result'])
            self.ui.resultTextLabel.setColor((status.loc['result'])['result'])

            self.ui.heartRateLabel.setColor(status.loc['heart_rate']['result'])
            self.ui.breathFreqLabel.setColor(status.loc['breath_freq']['result'])
            self.ui.variabilityIndexLabel.setColor(status.loc['variability_index']['result'])

            self.ui.startTimeAlphaLabel.setColor(status.loc['start_time']['result'])

        # self.createResultFile(file_path)

    def createResultFile(self, file_path):
        users.at[self.user, 'is_editing_result_files'] = 1

        result = [
            ['heart_rate', self.ui.heartRateLabel.color, self.ui.heartRateLabel.text()],
            ['breath_freq', self.ui.breathFreqLabel.color, self.ui.breathFreqLabel.text()],
            ['variability_index', self.ui.variabilityIndexLabel.color, self.ui.variabilityIndexLabel.text()],
            ['start_time', self.ui.startTimeAlphaLabel.color, self.ui.startTimeAlphaLabel.text()],
            ['result', self.ui.resultTextLabel.color, '']
        ]
        result_table = pd.DataFrame(result, columns=['ind', 'result', 'value'])
        filename, _ = os.path.splitext(file_path)
        # print(filename + '_r' + file_extension)
        result_table.to_csv(f"{filename}_r.csv", index=False)

        files = [self.ui.filesCombo.itemText(i) for i in range(self.ui.filesCombo.count())]
        filename = self.ui.filesCombo.currentText()
        print(filename)
        i = files.index(filename)
        self.ui.filesCombo.setItemData(i, QtGui.QColor(255, 255, 255), QtCore.Qt.BackgroundRole)

    def updateECG(self, file_path):
        file = os.path.split(file_path)[-1]
        filename, _ = os.path.splitext(file)
        self.ui.filesCombo.setCurrentText(filename)

        data = open_csv_file(file_path)
        properties = analysis_ecg(data['ecg'])

        self.ui.canvasECG.clear()
        self.ui.canvasECG.plot(properties['time'], data['ecg'][0])
        self.ui.canvasECG.save_data()
        self.ui.canvasECG.set_ylim()

        self.ui.canvasVar.clear()
        self.ui.canvasVar.plot(range(0, 2000, 50), properties['variability']['histogram'])
        self.ui.canvasVar.save_data()
        self.ui.canvasVar.set_ylim()

        self.ui.heartRateLabel.setText(str(properties['heart_rate']))
        self.ui.variabilityAmplitudeLabel.setText(str(properties['variability']['amplitude']))
        self.ui.variabilityIndexLabel.setText(str(properties['variability']['index']))
        self.ui.breathFreqLabel.setText(str(properties['breath']['freq']))

        return properties

    def updateEEG(self, file_path):
        file = os.path.split(file_path)[-1]
        filename, _ = os.path.splitext(file)

        data = open_csv_file(file_path)
        properties = analysis_eeg(data['eeg'])

        self.ui.canvasEEG.clear()
        self.ui.canvasEEG.plot(properties['time'], properties['filtered'])
        self.ui.canvasEEG.save_data()
        self.ui.canvasEEG.set_ylim()

        self.ui.canvasSpectrum.clear()
        self.ui.canvasSpectrum.plot(properties['spectrum']['freq'], properties['spectrum']['x'])
        self.ui.canvasSpectrum.save_data()
        self.ui.canvasSpectrum.set_ylim()

        self.ui.amplitudeAlphaLabel.setText(str(properties['spectrum']['amp']))
        self.ui.startTimeAlphaLabel.setText(str(properties['spectrum']['start_time']))

        return properties

    def changeEditingLabel(self, flag):
        self.ui.heartRateLabel.setEditable(flag)
        self.ui.variabilityAmplitudeLabel.setEditable(flag)
        self.ui.variabilityIndexLabel.setEditable(flag)
        self.ui.breathFreqLabel.setEditable(flag)

        self.ui.startTimeAlphaLabel.setEditable(flag)
        self.ui.amplitudeAlphaLabel.setEditable(flag)

        self.ui.resultTextLabel.setEditable(flag)

    def editingResultFileMode(self):
        self.ui.tab.setStyleSheet("background-color: rgb(255, 196, 197);\n"
                                  "alternate-background-color: rgb(170, 85, 255);")
        self.changeEditingLabel(True)
        self.ui.saveButton.setVisible(True)

    def saveResultFile(self):
        print('save')
        self.createResultFile(self.file_path)

    def editingResult(self):
        user = users.iloc[self.user]

        if self.ui.password.text() == user['password'] and self.file_path is not None:
            self.editingResultFileMode()
            self.ui.password.setStyleSheet("QLineEdit { background-color : #ffffff }")
        else:
            self.ui.password.setStyleSheet("QLineEdit { background-color : #c73636 }")

        self.ui.password.setText('')

    def createPassword(self):
        user = users.iloc[self.user]
        if user['password'] == 'None':
            if self.ui.password.text() != '':
                users.at[self.user, 'password'] = self.ui.password.text()
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
                users.at[self.user, 'password'] = 'None'
                self.ui.btnPassword.setText('Создать')
                self.ui.password.setStyleSheet("QLineEdit { background-color : #c73636 }")

        self.ui.password.setText('')

    def updateComports(self):
        available_ports = get_available_ports()
        self.ui.comportsCombo.clear()
        self.ui.comportsCombo.addItems(available_ports)

    def prediction(self):
        user = users.iloc[self.user]
        dir_path = user['dir_path']

        file = self.ui.filesCombo.currentText()
        filename_r = f"{file}_r.csv"
        files = [i for i in os.listdir(dir_path) if i.find('_r') != -1]

        ignor_index = None
        if os.path.exists(os.path.join(dir_path, filename_r)):
            ignor_index = files.index(filename_r)

        if int(user['is_editing_result_files']) == 1:
            models = fit(dir_path, ignor_index)
            save_models(dir_path, models)
        else:
            models = load_models(dir_path)

        data = {'heart_rate': self.ui.heartRateLabel.text(),
                'breath_freq': self.ui.breathFreqLabel.text(),
                'variability_index': self.ui.variabilityIndexLabel.text(),
                'start_time': self.ui.startTimeAlphaLabel.text()
                }
        status = {'heart_rate': 0,
                  'breath_freq': 0,
                  'variability_index': 0,
                  'start_time': 0,
                  'result': 0
                  }

        filename_p = crate_prediction_file(dir_path, file, data, status)

        status = predict(dir_path, filename_p, models)

        self.ui.resultTextLabel.setColor(status['result'])

        self.ui.heartRateLabel.setColor(status['heart_rate'])
        self.ui.breathFreqLabel.setColor(status['breath_freq'])
        self.ui.variabilityIndexLabel.setColor(status['variability_index'])

        self.ui.startTimeAlphaLabel.setColor(status['start_time'])

        crate_prediction_file(dir_path, file, data, status)

        print("prediction success")

    def saveSettings(self):
        users.at[self.user, 'timeECG'] = self.ui.timeECG.text()
        users.at[self.user, 'enableECG'] = int(self.ui.checkECG.isChecked())
        users.at[self.user, 'timeEEG'] = self.ui.timeEEG.text()
        users.at[self.user, 'enableEEG'] = int(self.ui.checkEEG.isChecked())
        users.at[self.user, 'enableGSR'] = int(self.ui.checkGSR.isChecked())

    def exit(self):
        self.saveSettings()
        users.to_csv('users.csv', index=False)
        self.close()
        self.dlg.close()

    def closeEvent(self, event):
        self.exit()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    application = Window()
    application.show()

    sys.exit(app.exec())
