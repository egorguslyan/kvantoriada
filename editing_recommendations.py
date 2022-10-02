from PyQt5 import QtWidgets
# from PyQt5 import QtCore, QtGui
from editing_recommendations_design import Ui_Dialog
# import sys
import pandas as pd
import os


class EditRecommendations(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super(EditRecommendations, self).__init__()
        self.setupUi(self)
        self.setModal(True)

        categories = ['Дети (0-11 лет)',  'Юниоры (12-17 лет)', 'Взрослые (18-34 лет)', 'Ветераны (35-99 лет)']
        self.ageCombo.insertItems(0, categories)

        parameters = ['Общее', 'ЧСС', 'Частота дыхания', 'Время появления альфа-ритма']
        self.parameterCombo.insertItems(0, parameters)

        statuses = ['Подавлен', 'Норма', 'Возбужден']
        self.statusCombo.insertItems(0, statuses)
        self.saveButton.clicked.connect(self.saveRecommendation)
        self.saveCombRecommendationButton.clicked.connect(self.saveCombRecommendation)
        self.deleteCombRecommendationButton.clicked.connect(self.deleteCombRecommendation)

        self.ageCombo.activated[str].connect(self.updateRecommendation)
        self.parameterCombo.activated[str].connect(self.updateRecommendation)
        self.statusCombo.activated[str].connect(self.updateRecommendation)
        self.updateCombRecommendationButton.clicked.connect(self.updateCombRecommendation)

        self.updateCombRecommendation()
        self.updateRecommendation('')

    def updateRecommendation(self, string):
        """
        Обновление поля текста рекомендации
        :param string:
        :return: None
        """
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
            recommendations = pd.read_csv(recommendation_file, delimiter=';')
        else:
            recommendations = pd.read_csv('recommendations.csv', delimiter=';')

        text = recommendations.set_index('ind').at[parameter, status]
        text_formatted = text.replace('<b>', '<').replace('</b>', '>')
        text_formatted = text_formatted.replace('<br>', '')

        self.textEdit.setText(text_formatted)

    def updateCombRecommendation(self):
        """
        Обновление поля текста рекомендации по комбинациям
        :return: None
        """
        heart_rate_status = self.heartRateSelectStatus.getStatus()
        breath_freq_status = self.breathFreqSelectStatus.getStatus()
        alpha_status = self.alphaSelectStatus.getStatus()
        combination = str(heart_rate_status) + str(breath_freq_status) + str(alpha_status)

        category = self.ageCombo.currentText()
        age = category[category.find('(') + 1:category.find(' лет')]
        recommendation_file = f"recommendations{age}.csv"
        if os.path.exists(recommendation_file):
            recommendations = pd.read_csv(recommendation_file, delimiter=';')
        else:
            recommendations = pd.read_csv('recommendations.csv', delimiter=';')

        if combination in recommendations['ind'].to_list():
            recommendations = recommendations.set_index('ind')
            text = recommendations.at[combination, 'normal']
            text_formatted = text.replace('<b>', '<').replace('</b>', '>')
            text_formatted = text_formatted.replace('<br>', '')

            self.textEdit_2.setText(text_formatted)
        else:
            self.textEdit_2.setText('Введите текст рекомендации')

    def saveRecommendation(self):
        """
        Сохранение изменений в выбранном файле рекомендаций по характеристике и состоянию
        :return: None
        """
        category = self.ageCombo.currentText()
        age = category[category.find('(') + 1:category.find(' лет')]

        parameter_text = self.parameterCombo.currentText()
        parameters = {
            'Общее': 'result',
            'ЧСС': 'heart_rate',
            'Частота дыхания': 'breath_freq',
            'Время появления альфа-ритма': 'alpha'
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

    def saveCombRecommendation(self):
        """
        Сохранение изменений в выбранном файле рекомендаций по комбинации состояний характеристик
        :return: None
        """
        heart_rate_status = self.heartRateSelectStatus.getStatus()
        breath_freq_status = self.breathFreqSelectStatus.getStatus()
        alpha_status = self.alphaSelectStatus.getStatus()
        combination = str(heart_rate_status) + str(breath_freq_status) + str(alpha_status)

        text = self.textEdit_2.toPlainText()
        i = 0
        while i < len(text) and (text.find('<', i) != -1 and text.find('>', text.find('<', i)) != -1):
            i = text.find('<', i)
            text = text[:i] + '<b>' + text[i + 1:]
            i += 3
            i = text.find('>', i)
            text = text[:i] + '</b>' + text[i + 1:]
            i += 4
        text_formatted = text

        category = self.ageCombo.currentText()
        age = category[category.find('(') + 1:category.find(' лет')]
        recommendation_file = f"recommendations{age}.csv"
        if os.path.exists(recommendation_file):
            recommendations = pd.read_csv(recommendation_file, delimiter=';')
        else:
            recommendations = pd.read_csv('recommendations.csv', delimiter=';')

        if combination in recommendations['ind'].to_list():
            recommendations = recommendations.set_index('ind')
            recommendations.at[combination, 'normal'] = text_formatted
        else:
            t = {'ind': combination,
                 'depressed': '-',
                 'normal': text_formatted,
                 'excited': '-'}
            new_comb = pd.DataFrame([list(t.values())], columns=list(t.keys()))
            recommendations = pd.concat([recommendations, new_comb], ignore_index=True).set_index('ind')

        recommendations.to_csv(recommendation_file, sep=';')

    def deleteCombRecommendation(self):
        """
        Удаление в выбранном файле рекомендаций по комбинации состояний характеристик
        :return:
        """
        heart_rate_status = self.heartRateSelectStatus.getStatus()
        breath_freq_status = self.breathFreqSelectStatus.getStatus()
        alpha_status = self.alphaSelectStatus.getStatus()
        combination = str(heart_rate_status) + str(breath_freq_status) + str(alpha_status)

        category = self.ageCombo.currentText()
        age = category[category.find('(') + 1:category.find(' лет')]
        recommendation_file = f"recommendations{age}.csv"
        if os.path.exists(recommendation_file):
            recommendations = pd.read_csv(recommendation_file, delimiter=';')
        else:
            recommendations = pd.read_csv('recommendations.csv', delimiter=';')

        if combination in recommendations['ind'].to_list():
            recommendations = recommendations.set_index('ind')
            recommendations.drop(index=[combination], axis=0, inplace=True)
        recommendations.to_csv(recommendation_file, sep=';')
