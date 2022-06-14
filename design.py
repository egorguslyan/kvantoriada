# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(1102, 583)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.table = QtWidgets.QTableWidget(self.centralwidget)
        self.table.setMaximumSize(QtCore.QSize(363, 16777215))
        self.table.setObjectName("table")
        self.table.setColumnCount(2)
        self.table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.NoBrush)
        item.setForeground(brush)
        self.table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(1, item)
        self.table.horizontalHeader().setDefaultSectionSize(30)
        self.table.horizontalHeader().setMinimumSectionSize(10)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.horizontalLayout.addWidget(self.table)
        self.tab = QtWidgets.QTabWidget(self.centralwidget)
        self.tab.setObjectName("tab")
        self.card = QtWidgets.QWidget()
        self.card.setObjectName("card")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.card)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.secondNameLable = QtWidgets.QLabel(self.card)
        self.secondNameLable.setEnabled(True)
        self.secondNameLable.setObjectName("secondNameLable")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.secondNameLable)
        self.secondNameEdit = QtWidgets.QLineEdit(self.card)
        self.secondNameEdit.setEnabled(False)
        self.secondNameEdit.setObjectName("secondNameEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.secondNameEdit)
        self.nameLable = QtWidgets.QLabel(self.card)
        self.nameLable.setObjectName("nameLable")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.nameLable)
        self.nameEdit = QtWidgets.QLineEdit(self.card)
        self.nameEdit.setEnabled(False)
        self.nameEdit.setObjectName("nameEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.nameEdit)
        self.middleNameLable = QtWidgets.QLabel(self.card)
        self.middleNameLable.setObjectName("middleNameLable")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.middleNameLable)
        self.middleNameEdit = QtWidgets.QLineEdit(self.card)
        self.middleNameEdit.setEnabled(False)
        self.middleNameEdit.setObjectName("middleNameEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.middleNameEdit)
        self.verticalLayout_4.addLayout(self.formLayout)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.birthdayLable = QtWidgets.QLabel(self.card)
        self.birthdayLable.setObjectName("birthdayLable")
        self.horizontalLayout_7.addWidget(self.birthdayLable)
        self.birthdayEdit = QtWidgets.QDateEdit(self.card)
        self.birthdayEdit.setEnabled(False)
        self.birthdayEdit.setObjectName("birthdayEdit")
        self.horizontalLayout_7.addWidget(self.birthdayEdit)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem)
        self.ageLable = QtWidgets.QLabel(self.card)
        self.ageLable.setObjectName("ageLable")
        self.horizontalLayout_7.addWidget(self.ageLable)
        self.ageNumberLable = QtWidgets.QLabel(self.card)
        self.ageNumberLable.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"")
        self.ageNumberLable.setFrameShape(QtWidgets.QFrame.Box)
        self.ageNumberLable.setObjectName("ageNumberLable")
        self.horizontalLayout_7.addWidget(self.ageNumberLable)
        self.verticalLayout_4.addLayout(self.horizontalLayout_7)
        self.line = QtWidgets.QFrame(self.card)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_4.addWidget(self.line)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem1)
        self.formLayout_3 = QtWidgets.QFormLayout()
        self.formLayout_3.setObjectName("formLayout_3")
        self.testLable = QtWidgets.QLabel(self.card)
        self.testLable.setObjectName("testLable")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.testLable)
        self.testDateLable = QtWidgets.QLabel(self.card)
        self.testDateLable.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.testDateLable.setFrameShape(QtWidgets.QFrame.Box)
        self.testDateLable.setObjectName("testDateLable")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.testDateLable)
        self.resultLable = QtWidgets.QLabel(self.card)
        self.resultLable.setObjectName("resultLable")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.resultLable)
        self.resultTextLable = QtWidgets.QLabel(self.card)
        self.resultTextLable.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.resultTextLable.setFrameShape(QtWidgets.QFrame.Box)
        self.resultTextLable.setObjectName("resultTextLable")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.resultTextLable)
        self.horizontalLayout_8.addLayout(self.formLayout_3)
        self.repeatButton = QtWidgets.QPushButton(self.card)
        self.repeatButton.setObjectName("repeatButton")
        self.horizontalLayout_8.addWidget(self.repeatButton)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem2)
        self.verticalLayout_4.addLayout(self.horizontalLayout_8)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem3)
        self.tab.addTab(self.card, "")
        self.ecg = QtWidgets.QWidget()
        self.ecg.setObjectName("ecg")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.ecg)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.ecgFilesCombo = QtWidgets.QComboBox(self.ecg)
        self.ecgFilesCombo.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.ecgFilesCombo.setObjectName("ecgFilesCombo")
        self.horizontalLayout_3.addWidget(self.ecgFilesCombo)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem4)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.variabilityMaxLable = QtWidgets.QLabel(self.ecg)
        self.variabilityMaxLable.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"border-color: rgb(0, 0, 0);")
        self.variabilityMaxLable.setFrameShape(QtWidgets.QFrame.Box)
        self.variabilityMaxLable.setObjectName("variabilityMaxLable")
        self.gridLayout.addWidget(self.variabilityMaxLable, 1, 2, 1, 1)
        self.haertRateLable = QtWidgets.QLabel(self.ecg)
        self.haertRateLable.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"border-color: rgb(0, 0, 0);")
        self.haertRateLable.setFrameShape(QtWidgets.QFrame.Box)
        self.haertRateLable.setObjectName("haertRateLable")
        self.gridLayout.addWidget(self.haertRateLable, 0, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.ecg)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 1, 0, 1, 1)
        self.variabilityMinLable = QtWidgets.QLabel(self.ecg)
        self.variabilityMinLable.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"border-color: rgb(0, 0, 0);")
        self.variabilityMinLable.setFrameShape(QtWidgets.QFrame.Box)
        self.variabilityMinLable.setObjectName("variabilityMinLable")
        self.gridLayout.addWidget(self.variabilityMinLable, 1, 1, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem5, 1, 3, 1, 1)
        self.label = QtWidgets.QLabel(self.ecg)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.ecg)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 2, 0, 1, 1)
        self.breathAmplitudeLable = QtWidgets.QLabel(self.ecg)
        self.breathAmplitudeLable.setStyleSheet("border-color: rgb(0, 0, 0);\n"
"background-color: rgb(255, 255, 255);")
        self.breathAmplitudeLable.setFrameShape(QtWidgets.QFrame.Box)
        self.breathAmplitudeLable.setObjectName("breathAmplitudeLable")
        self.gridLayout.addWidget(self.breathAmplitudeLable, 2, 1, 1, 1)
        self.verticalLayout_3.addLayout(self.gridLayout)
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem6)
        self.tab.addTab(self.ecg, "")
        self.eeg = QtWidgets.QWidget()
        self.eeg.setObjectName("eeg")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.eeg)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.tab.addTab(self.eeg, "")
        self.horizontalLayout.addWidget(self.tab)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.newUserButton = QtWidgets.QPushButton(self.centralwidget)
        self.newUserButton.setObjectName("newUserButton")
        self.horizontalLayout_2.addWidget(self.newUserButton)
        self.deleteUserButton = QtWidgets.QPushButton(self.centralwidget)
        self.deleteUserButton.setObjectName("deleteUserButton")
        self.horizontalLayout_2.addWidget(self.deleteUserButton)
        self.updateUserButton = QtWidgets.QPushButton(self.centralwidget)
        self.updateUserButton.setObjectName("updateUserButton")
        self.horizontalLayout_2.addWidget(self.updateUserButton)
        self.testButton = QtWidgets.QPushButton(self.centralwidget)
        self.testButton.setObjectName("testButton")
        self.horizontalLayout_2.addWidget(self.testButton)
        self.exitButton = QtWidgets.QPushButton(self.centralwidget)
        self.exitButton.setObjectName("exitButton")
        self.horizontalLayout_2.addWidget(self.exitButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.tab.setCurrentIndex(0)
        self.nameEdit.editingFinished.connect(self.middleNameEdit.setFocus)
        self.secondNameEdit.editingFinished.connect(self.nameEdit.setFocus)
        self.middleNameEdit.editingFinished.connect(self.birthdayEdit.setFocus)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.tab, self.secondNameEdit)
        MainWindow.setTabOrder(self.secondNameEdit, self.nameEdit)
        MainWindow.setTabOrder(self.nameEdit, self.middleNameEdit)
        MainWindow.setTabOrder(self.middleNameEdit, self.birthdayEdit)
        MainWindow.setTabOrder(self.birthdayEdit, self.repeatButton)
        MainWindow.setTabOrder(self.repeatButton, self.newUserButton)
        MainWindow.setTabOrder(self.newUserButton, self.deleteUserButton)
        MainWindow.setTabOrder(self.deleteUserButton, self.updateUserButton)
        MainWindow.setTabOrder(self.updateUserButton, self.exitButton)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        item = self.table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Спортсмен"))
        self.secondNameLable.setText(_translate("MainWindow", "Фамилия"))
        self.nameLable.setText(_translate("MainWindow", "Имя"))
        self.middleNameLable.setText(_translate("MainWindow", "Отчество"))
        self.birthdayLable.setText(_translate("MainWindow", "Дата рождения "))
        self.ageLable.setText(_translate("MainWindow", "Возраст"))
        self.ageNumberLable.setText(_translate("MainWindow", "какието цифры"))
        self.testLable.setText(_translate("MainWindow", "Дата теста"))
        self.testDateLable.setText(_translate("MainWindow", "какая-то дата"))
        self.resultLable.setText(_translate("MainWindow", "Результат"))
        self.resultTextLable.setText(_translate("MainWindow", "какойт-то результат"))
        self.repeatButton.setText(_translate("MainWindow", "Повторить"))
        self.tab.setTabText(self.tab.indexOf(self.card), _translate("MainWindow", "Карточка"))
        self.variabilityMaxLable.setText(_translate("MainWindow", "цифры"))
        self.haertRateLable.setText(_translate("MainWindow", "цифры"))
        self.label_5.setText(_translate("MainWindow", "Вариабельность (min, max):"))
        self.variabilityMinLable.setText(_translate("MainWindow", "цифры"))
        self.label.setText(_translate("MainWindow", "ЧСС:"))
        self.label_6.setText(_translate("MainWindow", "Дыхание (амплитуда): "))
        self.breathAmplitudeLable.setText(_translate("MainWindow", "цифры"))
        self.tab.setTabText(self.tab.indexOf(self.ecg), _translate("MainWindow", "ЭКГ"))
        self.tab.setTabText(self.tab.indexOf(self.eeg), _translate("MainWindow", "ЭЭГ"))
        self.newUserButton.setText(_translate("MainWindow", "Новый"))
        self.deleteUserButton.setText(_translate("MainWindow", "Удалить"))
        self.updateUserButton.setText(_translate("MainWindow", "Изменить"))
        self.testButton.setText(_translate("MainWindow", "Тест"))
        self.exitButton.setText(_translate("MainWindow", "Выход"))