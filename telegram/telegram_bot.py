import pandas as pd
import telebot
from base64 import b64decode
from threading import Thread

couches = None
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


class Bot(Thread):
    def __init__(self, tg_users, tg_couches, tg_doctors, token):
        super().__init__()
        self.tg_bot = telebot.TeleBot(b64decode(token).decode())
        self.users = tg_users
        self.couches = tg_couches
        self.doctors = tg_doctors
        self.state = {}
        self.readCouches()

    def run(self):

        @self.tg_bot.message_handler(commands=['logout'])
        def handle_logout(message):
            if message.chat.id in self.state.keys():
                if self.state[message.chat.id][0] == 2:
                    self.deleteTgId(self.state[message.chat.id][1])
                    self.tg_bot.send_message(message.chat.id, 'Вы успешно вышли из аккаунта')
                else:
                    self.tg_bot.send_message(message.chat.id, 'Вы не вошли в аккаунт')
                self.state.pop(message.chat.id)
            else:
                self.tg_bot.send_message(message.chat.id, 'Для входа в аккаунт тренера напишите "/login"')

        @self.tg_bot.message_handler(func=lambda message: message.chat.id in self.state.keys() and
                                     self.state[message.chat.id][0] == 2)
        def handle_logged(message):
            self.tg_bot.send_message(message.chat.id, 'Вы уже вошли в аккаунт под именем ' +
                                     self.state[message.chat.id][1] +
                                     '.\r\nЧтобы выйти из аккаунта, напишите "/logout"')

        @self.tg_bot.message_handler(commands=['login'])
        def handle_login(message):
            self.state[message.chat.id] = [0, None]
            self.tg_bot.send_message(message.chat.id, 'Введите свое имя и фамилию')

        @self.tg_bot.message_handler(content_types=['text'])
        def handle_text(message):
            if message.chat.id in self.state.keys():
                if self.state[message.chat.id] == [0, None]:
                    name = self.formatName(message.text)
                    if name in couches.get('couch_name').to_numpy():
                        self.state[message.chat.id] = [1, name]
                        self.tg_bot.send_message(message.chat.id, 'Введите ваш пароль')
                    else:
                        self.tg_bot.send_message(message.chat.id, 'Тренера с таким именем не существует')
                        self.state.pop(message.chat.id)

                elif self.state[message.chat.id][0] == 1:
                    if self.checkPassword(self.state[message.chat.id][1], message.text):
                        self.tg_bot.send_message(message.chat.id, 'Вы успешно вошли в аккаунт')
                        self.saveTgId(message.chat.id, self.state[message.chat.id][1])
                        self.state[message.chat.id] = [2, self.state[message.chat.id][1]]
                    else:
                        self.tg_bot.send_message(message.chat.id, 'Введен неверный пароль')
                        self.state.pop(message.chat.id)
            else:
                self.tg_bot.send_message(message.chat.id, 'Для входа в аккаунт тренера напишите "/login"')

        self.tg_bot.infinity_polling(interval=1)

    def formatName(self, name):
        name = name.title()
        if name not in self.couches.get('couch_name').to_numpy():
            swap_name = name.split()
            if len(swap_name) == 2:
                name = ' '.join(swap_name[::-1])
        return name

    def readCouches(self):
        for couch in couches.iterrows():
            if couch[1]['linked_account'] != 'None':
                self.state[int(couch[1]['linked_account'])] = [2, couch[1]['couch_name']]

    def checkPassword(self, couch_name, password):
        couch = self.couches.set_index('couch_name').loc[couch_name]
        return couch['couch_password'] == password

    def saveTgId(self, tg_id, couch_name):
        self.couches.set_index('couch_name', inplace=True)
        self.couches.at[couch_name, 'linked_account'] = str(tg_id)
        self.couches.reset_index(inplace=True)
        self.couches.to_csv('couches.csv', index=False)

    def deleteTgId(self, couch_name):
        self.couches.set_index('couch_name', inplace=True)
        self.couches.at[couch_name, 'linked_account'] = 'None'
        self.couches.reset_index(inplace=True)
        self.couches.to_csv('couches.csv', index=False)
