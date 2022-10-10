import pandas as pd
import telebot
from base64 import b64decode
from threading import Thread
from itertools import permutations

CONTENT_TYPES = ["text", "audio", "document", "photo", "sticker", "video", "video_note", "voice", "location", "contact"]


class Bot(Thread):
    def __init__(self, tg_users, tg_couches, tg_doctors, token):
        super().__init__()
        self.tg_bot = telebot.TeleBot(b64decode(token).decode())
        self.users = tg_users
        self.couches = tg_couches
        self.doctors = tg_doctors
        self.state = {}
        self.readAccounts()

    def run(self):
        @self.tg_bot.message_handler(func=lambda m: self.checkState(m, [None]), commands=['login', 'start'])
        def handle_login(message):
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            coach_btn = telebot.types.KeyboardButton('Тренер')
            doctor_btn = telebot.types.KeyboardButton('Врач')
            markup.add(coach_btn, doctor_btn)
            self.tg_bot.send_message(message.chat.id, text='Укажите вашу профессию', reply_markup=markup)
            self.state[message.chat.id] = ['wait_role', None]

        @self.tg_bot.message_handler(func=lambda m: self.checkState(m, [None]), content_types=CONTENT_TYPES)
        def handle_unlogged(message):
            self.tg_bot.send_message(message.chat.id, 'Для входа в аккаунт напишите "/login"')

        @self.tg_bot.message_handler(func=lambda m: self.checkState(m, ['wait_role']))
        def handle_role(message):
            markup = telebot.types.ReplyKeyboardRemove()
            if message.text == 'Тренер':
                self.state[message.chat.id][0] = 'c_wait_name'
                self.tg_bot.send_message(message.chat.id, 'Введите ваше ФИО', reply_markup=markup)
            elif message.text == 'Врач':
                self.state[message.chat.id][0] = 'd_wait_name'
                self.tg_bot.send_message(message.chat.id, 'Введите ваше ФИО', reply_markup=markup)

            else:
                self.tg_bot.send_message(message.chat.id, 'Ошибка', reply_markup=markup)
                self.state.pop(message.chat.id)

        @self.tg_bot.message_handler(func=lambda m: self.checkState(m, ['c_wait_name', 'd_wait_name']))
        def handle_username(message):
            names = []
            if self.state[message.chat.id][0][0] == 'c':
                names = self.couches.get('name').to_numpy()
            elif self.state[message.chat.id][0][0] == 'd':
                names = self.doctors.get('name').to_numpy()
            flag, name = self.checkName(message.text, names)

            if flag:
                self.state[message.chat.id] = [self.state[message.chat.id][0][0] + '_wait_pass', name]
                self.tg_bot.send_message(message.chat.id, 'Введите ваш пароль')
            else:
                self.tg_bot.send_message(message.chat.id, 'Пользователя с таким именем не существует')
                self.state.pop(message.chat.id)

        @self.tg_bot.message_handler(func=lambda m: self.checkState(m, ['c_wait_pass', 'd_wait_pass']))
        def handle_password(message):
            if self.checkPassword(self.state[message.chat.id], message.text):
                self.tg_bot.send_message(message.chat.id, 'Вы успешно вошли в аккаунт')
                self.saveTgId(message.chat.id, self.state[message.chat.id])
                self.state[message.chat.id][0] = self.state[message.chat.id][0][0] + '_logged'

            else:
                self.tg_bot.send_message(message.chat.id, 'Введен неверный пароль')
                self.state.pop(message.chat.id)

        @self.tg_bot.message_handler(func=lambda m: self.checkState(m, ['c_logged', 'd_logged']), commands=['logout'])
        def handle_logout(message):
            self.deleteTgId(self.state[message.chat.id])
            self.tg_bot.send_message(message.chat.id, 'Вы успешно вышли из аккаунта')
            self.state.pop(message.chat.id)

        @self.tg_bot.message_handler(func=lambda m: self.checkState(m, ['c_logged']),
                                     content_types=CONTENT_TYPES)
        def handle_logged_couch(message):
            if self.isDeleted(self.doctors, self.state[message.chat.id][1]):
                self.tg_bot.send_message(message.chat.id, 'Для входа в аккаунт напишите "/login"')
                self.state.pop(message.chat.id)
            else:
                self.tg_bot.send_message(message.chat.id, 'Вы уже вошли в аккаунт под именем ' +
                                         self.state[message.chat.id][1] +
                                         '.\r\nЧтобы выйти из аккаунта, напишите "/logout"')

        @self.tg_bot.message_handler(func=lambda m: self.checkState(m, ['d_logged']),
                                     content_types=CONTENT_TYPES)
        def handle_logged_doctor(message):
            if self.isDeleted(self.doctors, self.state[message.chat.id][1]):
                self.tg_bot.send_message(message.chat.id, 'Для входа в аккаунт напишите "/login"')
                self.state.pop(message.chat.id)
            else:
                self.tg_bot.send_message(message.chat.id, 'Вы уже вошли в аккаунт под именем ' +
                                         self.state[message.chat.id][1] +
                                         '.\r\nЧтобы выйти из аккаунта, напишите "/logout"')

        @self.tg_bot.message_handler(content_types=CONTENT_TYPES)
        def handle_misc(message):
            self.tg_bot.send_message(message.chat.id, 'Ошибка')
            self.state.pop(message.chat.id)

        self.tg_bot.infinity_polling(interval=1)

    def isDeleted(self, accounts, name):
        return accounts.set_index('name').at[name, 'linked_account'] == 'None'

    def checkState(self, message, states):
        if message.chat.id in self.state.keys():
            return self.state[message.chat.id][0] in states
        return None in states

    @staticmethod
    def checkName(name, names):
        name = name.title()
        if name in names:
            return True, name
        name_set = permutations(name.split())
        names_set = [tuple(set_name.split()) for set_name in names]

        for n in name_set:
            if n in names_set:
                return True, ' '.join(n)
        return False, None

    def readAccounts(self):
        for couch in self.couches.iterrows():
            if couch[1]['linked_account'] != 'None':
                self.state[int(couch[1]['linked_account'])] = ['c_logged', couch[1]['name']]

        for doctor in self.doctors.iterrows():
            if doctor[1]['linked_account'] != 'None':
                self.state[int(doctor[1]['linked_account'])] = ['d_logged', doctor[1]['name']]

    def checkPassword(self, account, password):
        acc_name = account[1]
        acc_type = account[0][0]

        if acc_type == 'c':
            couch = self.couches.set_index('name').loc[acc_name]
            return couch['password'] == password
        elif acc_type == 'd':
            doctor = self.doctors.set_index('name').loc[acc_name]
            return doctor['password'] == password

    def saveTgId(self, tg_id, account):
        acc_name = account[1]
        acc_type = account[0][0]

        if acc_type == 'c':
            self.couches.set_index('name', inplace=True)
            self.couches.at[acc_name, 'linked_account'] = str(tg_id)
            self.couches.reset_index(inplace=True)
            self.couches.to_csv('couches.csv', index=False)

        elif acc_type == 'd':
            self.doctors.set_index('name', inplace=True)
            self.doctors.at[acc_name, 'linked_account'] = str(tg_id)
            self.doctors.reset_index(inplace=True)
            self.doctors.to_csv('doctors.csv', index=False)

    def deleteTgId(self, account):
        acc_name = account[1]
        acc_type = account[0][0]

        if acc_type == 'c':
            self.couches.set_index('name', inplace=True)
            self.couches.at[acc_name, 'linked_account'] = 'None'
            self.couches.reset_index(inplace=True)
            self.couches.to_csv('couches.csv', index=False)

        elif acc_type == 'd':
            self.doctors.set_index('name', inplace=True)
            self.doctors.at[acc_name, 'linked_account'] = 'None'
            self.doctors.reset_index(inplace=True)
            self.doctors.to_csv('doctors.csv', index=False)

    def writeTg(self, user, table, target):
        if target == 'couch':
            receiver = self.couches.set_index('name').loc[user['couch_name']]
        elif target == 'doctor':
            receiver = self.doctors.set_index('name').loc[user['doctor_name']]
        else:
            return

        receiver_id = receiver['linked_account']
        if receiver_id != 'None':
            user_name = user['name'] + ' ' + user['surname']

            if target == 'couch':
                # recommendation_text = recommendation_text.replace('<br>', '\r\n')
                # recommendation_text = recommendation_text.replace('\r\n\r\n', '\r\n')
                result = table['result']['result']
                if result == 0:
                    results = 'Спортсмен находится в состоянии "предстартовой апатии"'
                elif result == 1:
                    results = 'Спортсмен находится в состоянии "боевой готовности"'
                elif result == 2:
                    results = 'Спортсмен находится в состоянии "предстартовой лихорадки"'
                else:
                    results = 'Error'
                text = user_name + ' прошел тестирование.\r\n\r\n<i>Результат:</i>\r\n' + results
                if user['doctor_name'] != 'None':
                    text += '\r\n\r\nТестирование провел врач ' + user['doctor_name']

            elif target == 'doctor':
                results = 'ЧСС: ' + str(int(table['heart_rate']['value'])) + ' уд/мин\r\nЧастота дыхания: ' \
                          + str(int(table['breath_freq']['value'])) + \
                          ' вдохов в минуту\r\nВариабельность сердечного ритма: ' \
                          + str(int(table['variability_index']['value'])) + '\r\n'
                alpha_time = int(table['start_time']['value'])
                if alpha_time >= 0:
                    results += 'Время до появления альфа-ритма: ' + str(alpha_time) + 'секунд'
                else:
                    results += 'Альфа ритм не обнаружен'
                text = user_name + ' прошел тестирование.\r\n\r\n<i>Полученные результаты:</i>\r\n' + results
                if user['couch_name'] != 'None':
                    text += '\r\n\r\nТестирование провел тренер ' + user['couch_name']

            else:
                text = 'Error'

            self.tg_bot.send_message(receiver_id, text, parse_mode='HTML')
