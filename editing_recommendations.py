from PyQt5 import QtWidgets, QtCore, QtGui
from editing_recommendations_design import Ui_Dialog
import sys
import pandas as pd
import os


class EditRecommendations(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super(EditRecommendations, self).__init__()
        self.setupUi(self)
        self.setModal(True)

        categories = ['Дети (0-11 лет)',  'Юниоры (12-17 лет)', 'Взрослые (18-34 лет)', 'Ветераны (35-99 лет)']
        self.ageCombo.insertItems(0, categories)

        parameters = ['Общее', 'ЧСС', 'Частота дыхания', 'Альфа-ритм']
        self.parameterCombo.insertItems(0, parameters)

        statuses = ['Подавлен', 'Норма', 'Возбужден']
        self.statusCombo.insertItems(0, statuses)
        self.saveButton.clicked.connect(self.saveRecommendation)

        self.ageCombo.activated[str].connect(self.updateRecommendation)
        self.parameterCombo.activated[str].connect(self.updateRecommendation)
        self.statusCombo.activated[str].connect(self.updateRecommendation)

    def updateRecommendation(self, str):
        '''
        Обновление поля текста рекомендации
        :param str:
        :return: None
        '''
        category = self.ageCombo.currentText()
        age = category[category.find('(') + 1:category.find(' лет')]

        parameter_text = self.parameterCombo.currentText()
        parameters = {
            'Общее': 'result',
            'ЧСС': 'heart_rate',
            'Частота дыхания': 'breath_freq',
            'Альфа-ритм': 'alpha'
        }
        parameter = parameters[parameter_text]

        status_text = self.statusCombo.currentText()
        statuses = {
            'Подавлен': 'depressed',
            'Норма': 'normal',
            'Возбужден': 'excited'
        }
        status = statuses[status_text]
        recommendation_file = f"recommendations{age}.csv"
        if os.path.exists(recommendation_file):
            recommendations = pd.read_csv(recommendation_file, delimiter=';').set_index('ind')
        else:
            recommendations = pd.read_csv('recommendations.csv', delimiter=';').set_index('ind')

        text = recommendations.at[parameter, status]
        text_formatted = text.replace('<b>', '<').replace('</b>', '>')
        text_formatted = text_formatted.replace('<br>', '')

        self.textEdit.setText(text_formatted)

    def saveRecommendation(self):
        '''
        Сохранение изменений в выбранном файле рекомендаций
        :return: None
        '''
        category = self.ageCombo.currentText()
        age = category[category.find('(') + 1:category.find(' лет')]

        parameter_text = self.parameterCombo.currentText()
        parameters = {
            'Общее': 'result',
            'ЧСС': 'heart_rate',
            'Частота дыхания': 'breath_freq',
            'Альфа-ритм': 'alpha'
        }
        parameter = parameters[parameter_text]

        status_text = self.statusCombo.currentText()
        statuses = {
            'Подавлен': 'depressed',
            'Норма': 'normal',
            'Возбужден': 'excited'
        }
        status = statuses[status_text]

        text = self.textEdit.toPlainText()
        i = 0
        while i < len(text) and (text.find('<', i) != -1 and text.find('>', text.find('<', i)) != -1):
            i = text.find('<', i)
            text = text[:i] + '<b>' + text[i + 1:]
            i += 3
            i = text.find('>', i)
            text = text[:i] + '</b>' + text[i + 1:]
            i += 4
        text_formatted = text + '<br>' + '<br>' * (parameter == 'result')

        recommendation_file = f"recommendations{age}.csv"
        if os.path.exists(recommendation_file):
            recommendations = pd.read_csv(recommendation_file, delimiter=';').set_index('ind')
        else:
            recommendations = pd.read_csv('recommendations.csv', delimiter=';').set_index('ind')
        recommendations.at[parameter, status] = text_formatted
        recommendations.to_csv(recommendation_file, sep=';')
