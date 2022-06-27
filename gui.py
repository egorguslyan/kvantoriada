from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QTableWidgetItem
from design import Ui_MainWindow
import sys
import pandas as pd
import os
import shutil
import time
import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from bluetooth_serial.read_serial import read
from analysis.ecg_analysis import analysis_ecg
from analysis.eeg_analysis import analysis_eeg
from analysis.signal_analysis import open_csv_file
from analysis.prediction import prediction

users_data = pd.read_csv('users.csv', delimiter=',')
users = pd.DataFrame(users_data)


class MplCanvas(FigureCanvas):
    def __init__(self, *args, **kwargs):
        self.fig = Figure()
        super(MplCanvas, self).__init__(self.fig, *args, **kwargs)

        self.ax = None
        self.data = None
        self.x = None
        self.y = None
        self.begin = 0
        self.end = 0

        self.fig.set_facecolor("#ffe6ea")

        hint = "двойной клик - приближение\n" \
               "правый клик - отдаление\n" \
               "колесико мыши - перемещение по оси времени"

        self.setToolTip(hint)

    def plot(self, x, y):
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        self.data = self.ax.plot(x, y)
        self.draw()

    def clear(self):
        self.fig.clear()
        self.draw()

    def get_xdata(self):
        return self.data[0].get_xdata()

    def get_ydata(self):
        return self.data[0].get_ydata()

    def scale_up(self, s, ratio):
        if self.begin is None or self.end is None:
            return

        length = self.end - self.begin
        s = int(s * length)
        self.end = self.begin + min(length, int(s + length * ratio / 2))
        self.begin = self.begin + max(0, int(s - length * ratio / 2))

        self.plot(self.x[self.begin:self.end], self.y[self.begin:self.end])
        self.set_ylim()

    def scale_down(self, s, ratio):
        if self.begin is None or self.end is None:
            return

        length = self.end - self.begin
        s = int(s * length)
        self.end = min(len(self.x), int(self.begin + s + length / ratio / 2))
        self.begin = max(0, int(self.begin + s - length / ratio / 2))

        self.plot(self.x[self.begin:self.end], self.y[self.begin:self.end])
        self.set_ylim()

    def scroll(self, direction):
        if self.begin is None or self.end is None:
            return

        length = self.end - self.begin
        if direction == -1:
            delta_begin = min(self.begin, int(length * 0.1))
        else:
            delta_begin = length

        if direction == 1:
            delta_end = min(len(self.x) - self.end, int(length * 0.1))
        else:
            delta_end = length

        self.begin += direction * min(delta_begin, delta_end)
        self.end += direction * min(delta_end, delta_begin)

        self.plot(self.x[self.begin:self.end], self.y[self.begin:self.end])
        self.set_ylim()

    def set_ylim(self):
        min_value = min(self.y)
        max_value = max(self.y)
        amplitude = max_value - min_value
        self.ax.set_ylim(min_value - amplitude * 0.1, max_value + amplitude * 0.1)
        self.draw()

    def save_data(self):
        self.x = self.get_xdata()
        self.y = self.get_ydata()
        self.begin = 0
        self.end = len(self.x)


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
        self.ui.canvasECG.mpl_connect("button_press_event", self.changeScaleECG)
        self.ui.canvasECG.mpl_connect("scroll_event", self.scrollingECG)

        self.ui.canvasEEG = MplCanvas()
        self.ui.verticalLayout_7.addWidget(self.ui.canvasEEG)
        self.ui.canvasEEG.mpl_connect("button_press_event", self.changeScaleEEG)
        self.ui.canvasEEG.mpl_connect("scroll_event", self.scrollingEEG)

        self.ui.canvasVar = MplCanvas()
        self.ui.verticalLayout_10.addWidget(self.ui.canvasVar)

        self.ui.btnPassword.clicked.connect(self.editingResult)

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

        self.ui.ageNumberLable.setText(str(age))

    def addNewUser(self):
        global users
        rows = self.ui.table.rowCount()
        date = QtCore.QDate.currentDate().toString('dd.MM.yyyy')

        dir_path = os.path.join('users', str(int(time.time())))
        os.mkdir(dir_path)

        user = [
            ['Name' + str(rows), 'Second' + str(rows), 'Middle' + str(rows), date, dir_path]
        ]
        user = pd.DataFrame(user, columns=['name', 'secondName', 'middleName', 'birthday', 'dir_path'])
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
                self.ui.ecgFilesCombo.addItems(files)
                self.ui.eegFilesCombo.addItems(files)

        self.ui.canvasECG.clear()

        self.ui.breathFreqLabel.setEditable(False)

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

        self.ui.testDateLable.setText(date)
        self.ui.resultTextLable.setText("тестируется")

        self.ui.ecgFilesCombo.addItem(date)
        self.ui.eegFilesCombo.addItem(date)

        if read('COM6', file_path):
            self.analysis(file_path)
        else:
            self.ui.resultTextLable.setText("не удалось подключиться")

    def selectFile(self, text):
        dir_path = users.iloc[self.user]['dir_path']
        file_path = os.path.join(dir_path, text)
        self.analysis(file_path)

    def analysis(self, file_path):
        ecg = self.updateECG(file_path)
        eeg = self.updateEEG(file_path)
        self.ui.resultTextLable.setText(prediction(ecg, eeg))

    def updateECG(self, file_path):
        data = open_csv_file(file_path)
        properties = analysis_ecg(data['ecg'])

        self.ui.canvasECG.clear()
        self.ui.canvasECG.plot(properties['time'], data['ecg'])
        self.ui.canvasECG.save_data()
        self.ui.canvasECG.set_ylim()

        self.ui.canvasVar.plot(range(0, 2000, 50), properties['variability']['histogram'])

        self.ui.haertRateLable.setText(str(properties['heart_rate']))
        self.ui.variabilityAmplitudeLable.setText(str(properties['variability']['amplitude']))
        self.ui.variabilityIndexLable.setText(str(properties['variability']['index']))
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

    def changeScaleECG(self, event):
        width = self.ui.canvasECG.frameGeometry().width()
        s = event.x / width
        if event.button == 1 and event.dblclick:
            self.ui.canvasECG.scale_up(s, 0.8)
        elif event.button == 3:
            self.ui.canvasECG.scale_down(s, 0.8)

    def changeScaleEEG(self, event):
        width = self.ui.canvasEEG.frameGeometry().width()
        s = event.x / width
        if event.button == 1 and event.dblclick:
            self.ui.canvasEEG.scale_up(s, 0.8)
        elif event.button == 3:
            self.ui.canvasEEG.scale_down(s, 0.8)

    def scrollingECG(self, event):
        self.ui.canvasECG.scroll(1 if event.button == 'up' else -1)

    def scrollingEEG(self, event):
        self.ui.canvasEEG.scroll(1 if event.button == 'up' else -1)

    def editingResult(self):
        self.ui.breathFreqLabel.setEditable(True)

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
