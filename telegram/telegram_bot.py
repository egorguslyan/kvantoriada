import pandas as pd
import telebot
from base64 import b64decode

tg_bot = telebot.TeleBot(b64decode('NTc4OTExODUyOTpBQUZoSi1yUEZhSnVqU2xGZXVBMmtpY3lJck5rOVpOOTM0dw==').decode())


def writeTg(user, file_path, recommendation_text, receiver):
    receiver_id = receiver['linked_account']
    if receiver_id != 'None':
        user_name = user['name'] + ' ' + user['surname']
        file_path = file_path[:-4] + '_r.csv'
        file_data = pd.read_csv(file_path, delimiter=',')
        file = pd.DataFrame(file_data)
        file = file.set_index('ind').loc[::, 'value']

        results = 'ЧСС: ' + str(int(file['heart_rate'])) + ' уд/мин\r\nЧастота дыхания: ' \
                  + str(int(file['breath_freq'])) + ' вдохов в минуту\r\nВариабельность сердечного ритма: ' \
                  + str(int(file['variability_index'])) + '\r\n'
        alpha_time = int(file['start_time'])
        if alpha_time >= 0:
            results += 'Время до появления альфа-ритма: ' + str(alpha_time) + 'секунд\r\n\r\n'
        else:
            results += 'Альфа ритм не обнаружен\r\n\r\n'

        recommendation_text = recommendation_text.replace('<br>', '\r\n')
        recommendation_text = recommendation_text.replace('\r\n\r\n', '\r\n')
        text = user_name + ' прошел тестирование.\r\n\r\n<i>Полученные результаты:</i>\r\n' + results \
            + '<i>Вывод:</i>\r\n' + recommendation_text

        tg_bot.send_message(receiver_id, text, parse_mode='HTML')
