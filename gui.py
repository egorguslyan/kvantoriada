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
from threading import Thread

# подключение собственных модулей
from bluetooth_serial.read_serial import read, get_available_ports
from analysis.ecg_analysis import analysis_ecg
from analysis.eeg_analysis import analysis_eeg
from analysis.signal_analysis import open_csv_file
from prediction.prior import prior_analysis
from prediction.prediction import fit, predict, crate_prediction_file, load_models, save_models
from editing_recommendations import EditRecommendations
from create_account import CreateAccount
# модуль холста для графиков
from mplcanvas import MplCanvas

test = True


# диалоговое окно с предупреждением
class WarningDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super(WarningDialog, self).__init__()
        self.setupUi(self)
        self.setModal(True)


# главное окно программы
class Window(QtWidgets.QMainWindow):
    def __init__(self, users, couches, doctors, tg_bot):
        # подготовка дизайна
        super(Window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.users = users
        self.couches = couches
        self.doctors = doctors
        self.bot = tg_bot

        # добавление событий
        self.ui.birthdayEdit.setMaximumDate(QtCore.QDate.currentDate())
        self.ui.birthdayEdit.editingFinished.connect(self.updateAge)
        self.ui.newUserButton.clicked.connect(self.addNewUser)
        self.ui.deleteUserButton.clicked.connect(self.deleteUser)
        self.ui.exitButton.clicked.connect(self.exit)
        self.ui.table.cellClicked.connect(self.chooseUser)
        self.ui.updateUserButton.clicked.connect(self.updateUser)
        self.ui.testButton.clicked.connect(self.testUser)
        self.ui.repeatButton.clicked.connect(self.testUser)
        self.ui.updateComButton.clicked.connect(self.updateComports)
        self.ui.filesCombo.activated[str].connect(self.selectFile)
        self.ui.saveButton.clicked.connect(self.saveResultFile)
        self.ui.deleteFile.clicked.connect(self.deleteFile)
        self.ui.predictionStatusButton.clicked.connect(self.prediction)
        self.ui.editRecommendationsButton.clicked.connect(self.editRecommendations)
        self.ui.btnPassword.clicked.connect(self.editingResult)
        self.ui.addNewDoctorButton.clicked.connect(self.addNewDoctor)
        self.ui.addNewCouchButton.clicked.connect(self.addNewCouch)

        # создание виджетов графиков
        self.ui.canvasECG = MplCanvas()  # ЭКГ
        self.ui.verticalLayout_8.addWidget(self.ui.canvasECG)

        self.ui.canvasEEG = MplCanvas()  # ЭЭГ
        self.ui.verticalLayout_7.addWidget(self.ui.canvasEEG)

        self.ui.canvasVar = MplCanvas()  # Гистограмма вариабельности сердечного ритма
        self.ui.verticalLayout_10.addWidget(self.ui.canvasVar)

        self.ui.canvasSpectrum = MplCanvas()  # спектр сигнала ЭЭГ
        self.ui.verticalLayout_6.addWidget(self.ui.canvasSpectrum)

        self.file_path = None
        self.updateComports()  # обновление списка COM-портов

        # создание диалоговых окон
        self.warningDialog = WarningDialog()
        self.editRecommendationsDialog = EditRecommendations()

        self.updateTable()  # обновление таблицы пользователей

        self.updateCouchesList()  # обновление списка тренеров
        self.updateDoctorList()  # обновление списка докторов
        self.ui.couchNameComboBox.setEnabled(False)
        self.ui.doctorNameComboBox.setEnabled(False)
        self.ui.addNewCouchButton.setEnabled(False)
        self.ui.addNewDoctorButton.setEnabled(False)

        # если есть пользователи, то загрузить карточку первого пользователя
        if not self.users.empty:
            self.user = 0
            self.updateCard()
        else:
            self.user = None

    def updateCouchesList(self):
        """
        Обновление списка тренеров
        """
        self.ui.couchNameComboBox.clear()
        self.ui.couchNameComboBox.addItem('Не выбрано')
        self.ui.couchNameComboBox.addItems(self.couches['couch_name'].to_list())

    def updateDoctorList(self):
        """
        Обновление списка докторов
        """
        self.ui.doctorNameComboBox.clear()
        self.ui.doctorNameComboBox.addItem('Не выбрано')
        self.ui.doctorNameComboBox.addItems(self.doctors['doctor_name'].to_list())

    def addNewCouch(self):
        """
        Создание нового тренера
        """
        dialog = CreateAccount('couch', self.couches)
        dialog.show()
        dialog.exec()
        self.couches = dialog.table
        self.bot.couches = self.couches
        self.updateCouchesList()

    def addNewDoctor(self):
        """
        Создание нового врача
        """
        dialog = CreateAccount('doctor', self.doctors)
        dialog.show()
        dialog.exec()
        self.doctors = dialog.table
        self.bot.doctors = self.doctors
        self.updateDoctorList()

    def updateAge(self):
        """
        расчет возраста пользователя
        :return: None
        """
        birthday = self.ui.birthdayEdit.date()
        now = QtCore.QDate.currentDate()

        age = now.year() - birthday.year()
        if now.month() < birthday.month():
            age -= 1
        elif now.month() == birthday.month() and now.day() < birthday.day():
            age -= 1

        self.ui.ageNumberLabel.setText(str(age))

    def addNewUser(self):
        """
        создание нового пользователя
        :return: None
        """
        rows = self.ui.table.rowCount()
        date = QtCore.QDate.currentDate().toString('dd.MM.yyyy')

        dir_path = os.path.normpath(os.path.join('users', str(int(time.time()))))
        os.mkdir(dir_path)

        user = {
            'name': 'Name' + str(rows),
            'surname': 'Surname' + str(rows),
            'middleName': 'Middle' + str(rows),
            'birthday': date,
            'dir_path': dir_path,
            'doctor_name': 'None',
            'last_result': 'None',
            'is_editing_result_files': 0,
            'enableECG': 1,
            'timeECG': 10,
            'enableEEG': 1,
            'timeEEG': 10,
            'enableGSR': 1,
            'couch_name': 'None'
        }
        user = pd.DataFrame([list(user.values())], columns=list(user.keys()))
        self.users = pd.concat([self.users, user], ignore_index=True)
        self.bot.users = self.users

        self.updateTable()

    def deleteUser(self):
        """
        удаление выбранного пользователя и всех его данных
        :return: None
        """
        row = self.ui.table.currentRow()
        if row > -1:
            user = self.users.iloc[self.user]
            shutil.rmtree(user['dir_path'])  # удаление папки пользователя

            self.users.drop(index=[row], axis=0, inplace=True)
            self.users.reset_index(drop=True, inplace=True)

            if len(self.users) > 0:
                self.user = 0
                self.updateCard()
            else:
                self.user = None

            self.updateTable()
            self.ui.table.selectionModel().clearCurrentIndex()

    def chooseUser(self):
        """
        выбор пользователя
        :return: None
        """
        self.saveSettings()
        row = self.ui.table.currentRow()
        self.user = row
        self.updateCard()

    def updateCard(self):
        """
        обновление карточки пользователя
        :return: None
        """
        # очищение графиков
        self.ui.canvasECG.clear()
        self.ui.canvasEEG.clear()
        self.ui.canvasVar.clear()
        self.ui.canvasSpectrum.clear()

        # сброс всех изменений
        self.editingResultFileMode(False)
        self.clearLabels()
        self.file_path = None
        self.ui.password.setStyleSheet('QLineEdit { background-color : #ffffff }')

        self.ui.tab.setCurrentIndex(0)

        self.ui.recommendationsText.setText('')

        # если выбран пользователь, загрузить его данные
        if self.user is not None:
            user = self.users.iloc[self.user]
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
            # создание списка файлов с сигналами
            if files:
                for file in files:
                    if not re.search(r'\d\d.\d\d.\d{4} \d\d-\d\d-\d\d_\w', file) \
                            and re.search(r'\d\d.\d\d.\d{4} \d\d-\d\d-\d\d', file):
                        filename, _ = os.path.splitext(file)
                        self.ui.filesCombo.addItem(filename)

                        # в зависимости от отмеченного результата изменить фон записи
                        color = QtGui.QColor(198, 198, 198)
                        if files.count(f'{filename}_r.csv') != 0:
                            r_file = os.path.normpath(os.path.join(user['dir_path'], f"{filename}_r.csv"))
                            result = pd.read_csv(r_file, delimiter=',').set_index('ind').loc['result']['result']
                            if result == 2:
                                color = QtGui.QColor(227, 138, 138)  # red
                            elif result == 1:
                                color = QtGui.QColor(201, 245, 142)  # green
                            else:
                                color = QtGui.QColor(155, 151, 255)  # blue
                        self.ui.filesCombo.setItemData(i, color, QtCore.Qt.BackgroundRole)
                        i += 1
            self.ui.deleteFile.setVisible(False)
            self.ui.predictionStatusButton.setVisible(False)

            # загрузка последней записи
            combo_box = self.ui.filesCombo
            files_combo = [combo_box.itemText(i) for i in range(combo_box.count())]
            if files_combo:
                self.selectFile(files_combo[-1])
                self.ui.testDateLabel.setText(files_combo[-1])

            # Очистка поля ввода пароля врача
            self.ui.password.setText('')

            # загрузка предыдущих настроек пользователя
            self.ui.checkECG.setChecked(bool(user['enableECG']))
            self.ui.timeECG.setValue(int(user['timeECG']))
            self.ui.checkEEG.setChecked(bool(user['enableEEG']))
            self.ui.timeEEG.setValue(int(user['timeEEG']))
            self.ui.checkGSR.setChecked(bool(user['enableGSR']))

            # Отображение тренера и доктора
            if user['couch_name'] == 'None':
                self.ui.couchNameComboBox.setCurrentIndex(0)
            else:
                self.ui.couchNameComboBox.setCurrentIndex(self.couches['couch_name'].to_list().index(user['couch_name'])
                                                          + 1)

            if user['doctor_name'] == 'None':
                self.ui.doctorNameComboBox.setCurrentIndex(0)
            else:
                self.ui.doctorNameComboBox.setCurrentIndex(self.doctors['doctor_name'].to_list().index(
                    user['doctor_name']) + 1)

    def clearLabels(self):
        """
        очищение Label-ов результатов от записей
        :return: None
        """
        self.ui.heartRateLabel.clear()
        self.ui.breathFreqLabel.clear()
        self.ui.variabilityIndexLabel.clear()
        self.ui.variabilityAmplitudeLabel.clear()

        self.ui.amplitudeAlphaLabel.clear()
        self.ui.startTimeAlphaLabel.clear()

        self.ui.resultTextLabel.clear()

    def updateTable(self):
        """
        обновление таблицы пользователей
        :return: None
        """
        self.ui.table.clear()
        # self.ui.table.setHorizontalHeaderLabels(['', 'Спортсмен'])

        if len(self.users) > 0:
            self.ui.table.setRowCount(len(self.users))
            for i in range(len(self.users)):
                user = self.users.iloc[i]
                name = ' '.join([user['surname'], user['name'], user['middleName']])
                name = QTableWidgetItem(name)
                name.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )
                self.ui.table.setItem(i, 0, name)

    def updatingUserMode(self, flag):
        """
        режим изменения данных пользователя
        :param flag:
        :return: None
        """
        self.ui.surnameEdit.setReadOnly(flag)
        self.ui.nameEdit.setReadOnly(flag)
        self.ui.middleNameEdit.setReadOnly(flag)
        self.ui.birthdayEdit.setReadOnly(flag)
        self.ui.couchNameComboBox.setEnabled(not flag)
        self.ui.doctorNameComboBox.setEnabled(not flag)
        self.ui.newUserButton.setEnabled(flag)
        self.ui.deleteUserButton.setEnabled(flag)
        self.ui.testButton.setEnabled(flag)
        self.ui.table.setEnabled(flag)
        self.ui.repeatButton.setEnabled(flag)
        self.ui.predictionStatusButton.setEnabled(flag)
        self.ui.deleteFile.setEnabled(flag)
        self.ui.btnPassword.setEnabled(flag)
        self.ui.saveButton.setEnabled(flag)
        self.ui.addNewCouchButton.setEnabled(not flag)
        self.ui.addNewDoctorButton.setEnabled(not flag)

    def updateUser(self):
        """
        изменение данных пользователя
        :return: None
        """
        if self.ui.updateUserButton.text() == 'Изменить':
            self.updatingUserMode(False)
            self.ui.updateUserButton.setText('Сохранить')
        else:
            if self.ui.surnameEdit.text() != '':
                self.users.at[self.user, 'surname'] = self.ui.surnameEdit.text()
                self.ui.surnameEdit.setStyleSheet('QLineEdit { background-color : #ffffff; }')
            else:
                self.ui.surnameEdit.setStyleSheet('QLineEdit { background-color : #c73636; }')
                return

            if self.ui.nameEdit.text() != '':
                self.users.at[self.user, 'name'] = self.ui.nameEdit.text()
                self.ui.nameEdit.setStyleSheet('QLineEdit { background-color : #ffffff; }')
            else:
                self.ui.nameEdit.setStyleSheet('QLineEdit { background-color : #c73636; }')
                return

            if self.ui.middleNameEdit.text() != '':
                self.users.at[self.user, 'middleName'] = self.ui.middleNameEdit.text()
                self.ui.middleNameEdit.setStyleSheet('QLineEdit { background-color : #ffffff; }')
            else:
                self.ui.middleNameEdit.setStyleSheet('QLineEdit { background-color : #c73636; }')
                return

            self.users.at[self.user, 'birthday'] = self.ui.birthdayEdit.dateTime().toString('dd.MM.yyyy')
            if self.ui.couchNameComboBox.currentText() == 'Не выбрано':
                self.users.at[self.user, 'couch_name'] = 'None'
            else:
                self.users.at[self.user, 'couch_name'] = self.ui.couchNameComboBox.currentText()

            if self.ui.doctorNameComboBox.currentText() == 'Не выбрано':
                self.users.at[self.user, 'doctor_name'] = 'None'
            else:
                self.users.at[self.user, 'doctor_name'] = self.ui.doctorNameComboBox.currentText()

            self.updateTable()

            self.updatingUserMode(True)
            self.ui.updateUserButton.setText('Изменить')

    def testUser(self):
        """
        тестирование пользователя
        :return: None
        """
        time_format = '%d.%m.%Y %H-%M-%S'

        user = self.users.iloc[self.user]
        dir_path = user['dir_path']
        # проверка на повторность записи. Если с предыдущей записи прошло менее 2 минут, перезаписать
        date = datetime.datetime.now().strftime(time_format)
        files = [self.ui.filesCombo.itemText(i) for i in range(self.ui.filesCombo.count())]
        if files:
            last_file = files[-1]
            if (datetime.datetime.now() - datetime.datetime.strptime(last_file, time_format)).seconds < 120:
                if os.path.exists(os.path.normpath(os.path.join(dir_path, f"{last_file}.csv"))):
                    os.remove(os.path.normpath(os.path.join(dir_path, f"{last_file}.csv")))
                self.ui.filesCombo.removeItem(self.ui.filesCombo.count() - 1)
                # print(datetime.datetime.now() - datetime.datetime.strptime(last_file, time_format))

        file_path = os.path.normpath(os.path.join(dir_path, f"{date}.csv"))

        self.ui.testDateLabel.setText(date)

        self.ui.filesCombo.addItem(date)
        i = self.ui.filesCombo.count() - 1
        # print(i)
        self.ui.filesCombo.setItemData(i, QtGui.QColor(198, 198, 198), QtCore.Qt.BackgroundRole)

        time_ecg = int(self.ui.timeECG.text())
        time_eeg = int(self.ui.timeEEG.text())
        enable_ecg = int(self.ui.checkECG.isChecked())
        enable_eeg = int(self.ui.checkEEG.isChecked())
        enable_gsr = int(self.ui.checkGSR.isChecked())

        # подключение к модулю с датчиками
        if read(self.ui.comportsCombo.currentText(), file_path,
                timeECG=time_ecg, timeEEG=time_eeg,
                enableECG=enable_ecg, enableEEG=enable_eeg, enableGSR=enable_gsr):
            self.analysis(file_path)

            if user['couch_name'] != 'None':
                couch = self.couches.set_index('couch_name').loc[user['couch_name']]
                self.bot.writeTg(user, file_path, couch)

            if user['doctor_name'] != 'None':
                doctor = self.doctors.set_index('doctor_name').loc[user['doctor_name']]
                self.bot.writeTg(user, file_path, doctor)

            self.users.at[self.user, 'last_result'] = self.ui.resultTextLabel.get_result()
        else:

            if test:
                file_path = 'users/1656666431/01.07.2022 14-41-11.csv'
                self.analysis(file_path)
                if user['couch_name'] != 'None':
                    couch = self.couches.set_index('couch_name').loc[user['couch_name']]
                    self.bot.writeTg(user, file_path, couch)
                if user['doctor_name'] != 'None':
                    doctor = self.doctors.set_index('doctor_name').loc[user['doctor_name']]
                    self.bot.writeTg(user, file_path, doctor)

            self.ui.resultTextLabel.setText('Не удалось подключиться')
            self.ui.filesCombo.removeItem(self.ui.filesCombo.count() - 1)

    def selectFile(self, file):
        """
        выбор файла в списке файлов
        :param file: имя файла (без разрешения и пути)
        :return: None
        """
        dir_path = self.users.iloc[self.user]['dir_path']
        filename = os.path.normpath(os.path.join(dir_path, file))
        self.analysis(f"{filename}.csv")

    def deleteFile(self):
        """
        удаление выбранного файла сигнала
        :return: None
        """
        user = self.users.iloc[self.user]

        filename = self.ui.filesCombo.currentText()
        file = f"{filename}.csv"
        file_path = os.path.normpath(os.path.join(user['dir_path'], file))

        if os.path.exists(file_path):
            os.remove(file_path)

            r_file = f"{filename}_r.csv"
            r_file_path = os.path.normpath(os.path.join(user['dir_path'], r_file))
            if os.path.exists(r_file_path):
                os.remove(r_file_path)

            p_file = f"{filename}_p.csv"
            p_file_path = os.path.normpath(os.path.join(user['dir_path'], p_file))
            if os.path.exists(p_file_path):
                os.remove(p_file_path)

        files = [self.ui.filesCombo.itemText(i) for i in range(self.ui.filesCombo.count())]
        self.ui.filesCombo.removeItem(files.index(filename))

    def analysis(self, file_path):
        """
        анализ сигналов и вывод состояний
        :param file_path: полное имя файла
        :return: str: рекомендации спортсмену
        """
        # self.ui.predictionStatusButton.setVisible(True)
        self.ui.deleteFile.setVisible(True)

        self.file_path = file_path

        file = os.path.split(file_path)[-1]
        filename, _ = os.path.splitext(file)
        self.ui.filesCombo.setCurrentText(filename)

        ecg = self.updateECG(file_path)
        eeg = self.updateEEG(file_path)

        filename, _ = os.path.splitext(file_path)
        r_file = f"{filename}_r.csv"
        p_file = f"{filename}_p.csv"
        # проверка на наличие файла с размеченными результатами
        if not os.path.exists(r_file):  # and not os.path.exists(p_file):
            cnt_r_files = sum(map(lambda x: x.find('_r') != -1, os.listdir(self.users.at[self.user, 'dir_path'])))
            # проверка на количество помеченных файлов
            if cnt_r_files < 5:
                self.warningDialog.show()
                self.warningDialog.exec()

                status = prior_analysis(ecg, eeg)
                self.ui.resultTextLabel.setColor(status['result'])

                self.ui.heartRateLabel.setColor(status['heart_rate'])
                self.ui.breathFreqLabel.setColor(status['breath']['freq'])
                self.ui.variabilityIndexLabel.setColor(status['variability']['index'])

                self.ui.startTimeAlphaLabel.setColor(status['spectrum']['start_time'])
            else:
                self.prediction()  # машинное обучение на размеченных файлах

        else:
            # загрузка результатов
            if os.path.exists(r_file):
                status = pd.read_csv(r_file, delimiter=',')
            else:
                status = pd.read_csv(p_file, delimiter=',')
            status.set_index('ind', inplace=True)
            # print(status)
            # print(status.loc['result'])
            self.ui.resultTextLabel.setColor((status.loc['result'])['result'])

            self.ui.heartRateLabel.setColor(status.loc['heart_rate']['result'])
            self.ui.breathFreqLabel.setColor(status.loc['breath_freq']['result'])
            self.ui.variabilityIndexLabel.setColor(status.loc['variability_index']['result'])

            self.ui.startTimeAlphaLabel.setColor(status.loc['start_time']['result'])

        # self.createResultFile(file_path)
        recommendation_text = self.recommendations()  # вывод рекомендаций
        self.ui.recommendationsText.setText(recommendation_text)

    def createResultFile(self, file_path):
        """
        создание результирующего файла
        :param file_path: имя файла с путем
        :return: None
        """
        self.users.at[self.user, 'is_editing_result_files'] = 1

        # создание файла
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

        # изменение фона записи в зависимости от отмеченного результата
        files = [self.ui.filesCombo.itemText(i) for i in range(self.ui.filesCombo.count())]
        filename = self.ui.filesCombo.currentText()
        result = self.ui.resultTextLabel.color
        if result == 2:
            color = QtGui.QColor(227, 138, 138)
        elif result == 1:
            color = QtGui.QColor(201, 245, 142)
        else:
            color = QtGui.QColor(155, 151, 255)
        i = files.index(filename)
        self.ui.filesCombo.setItemData(i, color, QtCore.Qt.BackgroundRole)

    def updateECG(self, file_path):
        """
        обновление графиков ЭКГ
        :param file_path: имя файла
        :return: None
        """
        # чтение сигнала ЭКГ из файла и его анализ
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

        if properties['diff_heart_rate'] == '-':
            self.ui.decreaseHeartRate.setVisible(False)
            self.ui.decreaseHeartRateLabel.setVisible(False)
            self.ui.decreaseHeartRateMeasure.setVisible(False)
        else:
            self.ui.decreaseHeartRate.setVisible(True)
            self.ui.decreaseHeartRateLabel.setVisible(True)
            self.ui.decreaseHeartRateMeasure.setVisible(True)
            self.ui.decreaseHeartRateLabel.setText(properties['diff_heart_rate'])

        return properties

    def updateEEG(self, file_path):
        """
        обновление графиков ЭЭГ
        :param file_path: имя файла
        :return: None
        """
        # чтение сигнала ЭЭГ из файла и его анализ
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
        """
        режим изменения Label-ов с результатами
        :param flag:
        :return: None
        """
        self.ui.heartRateLabel.setEditable(flag)
        self.ui.variabilityAmplitudeLabel.setEditable(flag)
        self.ui.variabilityIndexLabel.setEditable(flag)
        self.ui.breathFreqLabel.setEditable(flag)

        self.ui.startTimeAlphaLabel.setEditable(flag)
        self.ui.amplitudeAlphaLabel.setEditable(flag)

        self.ui.resultTextLabel.setEditable(flag)

    def editingResultFileMode(self, flag):
        """
        режим изменения результатов
        :return: None
        """
        if flag:
            self.ui.tab.setStyleSheet('background-color: rgb(255, 196, 197);\n'
                                      'alternate-background-color: rgb(170, 85, 255);')
        else:
            self.ui.tab.setStyleSheet('background-color: rgb(255, 230, 234);\n'
                                      'alternate-background-color: rgb(170, 85, 255);')
        self.changeEditingLabel(flag)
        self.ui.saveButton.setVisible(flag)

        self.ui.editRecommendationsButton.setVisible(flag)

    def saveResultFile(self):
        """
        сохранение изменений результирующего файла
        :return: None
        """
        self.createResultFile(self.file_path)

    def editingResult(self):
        """
        Проверка пароля для режима изменения результатов
        :return: None
        """
        user = self.users.iloc[self.user]
        if user['doctor_name'] == 'None':
            self.ui.password.setText('')
            return

        if self.ui.password.text() == self.doctors.set_index('doctor_name').at[user['doctor_name'], 'doctor_password'] \
                and self.file_path is not None:
            self.editingResultFileMode(True)
            self.ui.password.setStyleSheet('QLineEdit { background-color : #ffffff }')
        else:
            self.ui.password.setStyleSheet('QLineEdit { background-color : #c73636 }')

        self.ui.password.setText('')

    def updateComports(self):
        """
        Функция обновления доступных COM-портов
        :return: None
        """
        available_ports = get_available_ports()
        self.ui.comportsCombo.clear()
        self.ui.comportsCombo.addItems(available_ports)

    def prediction(self):
        """
        Функция предсказания результата при помощи машинного обучения
        :return: None
        """
        user = self.users.iloc[self.user]
        dir_path = user['dir_path']

        file = self.ui.filesCombo.currentText()
        filename_r = f"{file}_r.csv"
        files = [i for i in os.listdir(dir_path) if i.find('_r') != -1]

        ignor_index = None
        if os.path.exists(os.path.normpath(os.path.join(dir_path, filename_r))):
            ignor_index = files.index(filename_r)

        # загрузка уже обученных моделей
        # или создание и сохранение новых в зависимости от того, создавались ли еще результирующие файлы
        if int(user['is_editing_result_files']) == 1:
            models = fit(dir_path, ignor_index)
            save_models(dir_path, models)
            self.users.at[self.user, 'is_editing_result_files'] = 0
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

    def saveSettings(self):
        """
        Сохранение настроек пользователя
        :return: None
        """
        self.users.at[self.user, 'timeECG'] = self.ui.timeECG.text()
        self.users.at[self.user, 'enableECG'] = int(self.ui.checkECG.isChecked())
        self.users.at[self.user, 'timeEEG'] = self.ui.timeEEG.text()
        self.users.at[self.user, 'enableEEG'] = int(self.ui.checkEEG.isChecked())
        self.users.at[self.user, 'enableGSR'] = int(self.ui.checkGSR.isChecked())

    def recommendations(self):
        """
        Выдача рекомендаций
        :return: str: рекомендации спортсмену
        """
        recommend_files = [i for i in os.listdir('.') if i.find('recommendations') != -1 and i.find('-') != -1]
        recommend_file = 'recommendations.csv'
        if recommend_files:
            for i in recommend_files:
                min_age = int(i[15:i.find('-')])
                max_age = int(i[i.find('-') + 1:i.find('.')])
                if min_age <= int(self.ui.ageNumberLabel.text()) <= max_age:
                    recommend_file = i

        recommend = pd.read_csv(recommend_file, delimiter=';')
        combinations = [i for i in recommend['ind'].to_list() if i.isdigit()]

        recommend.set_index('ind', inplace=True)
        text = ''
        result = self.ui.resultTextLabel.get_result()
        text += recommend.loc['result', result]
        heart_rate = self.ui.heartRateLabel.get_result()
        text += recommend.loc['heart_rate', heart_rate]
        breath_freq = self.ui.breathFreqLabel.get_result()
        text += recommend.loc['breath_freq', breath_freq]
        alpha = self.ui.startTimeAlphaLabel.get_result()
        text += recommend.loc['alpha', alpha]

        results = {
            'depressed': '1',
            'normal': '2',
            'excited': '3'
        }
        heart_rate_status = results[heart_rate]
        breath_freq_status = results[breath_freq]
        alpha_status = results[alpha]

        if combinations:
            max_cnt = 0
            recommend_text = recommend.at[combinations[0], 'normal']

            for comb in combinations:
                cnt = 0
                if comb[0] == '0':
                    cnt += 1
                elif comb[0] == heart_rate_status:
                    cnt += 2

                if comb[1] == '0':
                    cnt += 1
                elif comb[1] == breath_freq_status:
                    cnt += 2

                if comb[2] == '0':
                    cnt += 1
                elif comb[2] == alpha_status:
                    cnt += 2

                if max_cnt < cnt:
                    max_cnt = cnt
                    recommend_text = recommend.at[comb, 'normal']

            if max_cnt > 3:
                text = recommend_text

        if self.ui.decreaseHeartRateLabel.isVisible() and int(self.ui.decreaseHeartRateLabel.text()) > 10:
            text += '<br>Отмечено снижение пульса за время исследования, ' \
                    'что может свидетельствовать о способности саморегуляции спортсменом своего состояния'
        elif self.ui.decreaseHeartRateLabel.isVisible() and int(self.ui.decreaseHeartRateLabel.text()) < -10:
            text += '<br>Отмечено повышение пульса за время исследования, ' \
                    'что может свидетельствовать о волнении спортсмена'

        return text

    def editRecommendations(self):
        """
        Вызов окна редактирования рекомендаций
        :return: None
        """
        self.editRecommendationsDialog.show()
        self.editRecommendationsDialog.exec()
        recommendation_text = self.recommendations()
        self.ui.recommendationsText.setText(recommendation_text)

    def exit(self):
        """
        Закрытие главного окна
        :return: None
        """
        self.saveSettings()
        self.users.to_csv('users.csv', index=False)  # сохранение таблицы пользователей
        self.couches.to_csv('couches.csv', index=False)  # сохранение таблицы тренеров
        self.doctors.to_csv('doctors.csv', index=False)  # сохранение таблицы врачей
        self.close()
        self.warningDialog.close()
        self.editRecommendationsDialog.close()
        sys.exit()

    def closeEvent(self, event):
        self.exit()


class Gui(Thread):
    def __init__(self, users, couches, doctors, bot):
        super().__init__()
        self.users = users
        self.couches = couches
        self.doctors = doctors
        self.bot = bot

    def run(self):
        app = QtWidgets.QApplication([])
        application = Window(self.users, self.couches, self.doctors, self.bot)
        application.show()
        sys.exit(app.exec())
