import pandas as pd
import telebot
from base64 import b64decode
from threading import Thread
from itertools import permutations

CONTENT_TYPES = ["text", "audio", "document", "photo", "sticker", "video", "video_note", "voice", "location", "contact",
                 "new_chat_members", "left_chat_member", "new_chat_title", "new_chat_photo", "delete_chat_photo",
                 "group_chat_created", "supergroup_chat_created", "channel_chat_created", "migrate_to_chat_id",
                 "migrate_from_chat_id", "pinned_message"]


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

        @self.tg_bot.message_handler(func=lambda m: self.checkState(m, None), commands=['login', 'start'])
        def handle_login(message):
            self.state[message.chat.id] = ['wait_name', None]
            self.tg_bot.send_message(message.chat.id, 'Введите свое имя и фамилию')

        @self.tg_bot.message_handler(func=lambda m: self.checkState(m, None), content_types=CONTENT_TYPES)
        def handle_unlogged(message):
            self.tg_bot.send_message(message.chat.id, 'Для входа в аккаунт напишите "/login"')

        @self.tg_bot.message_handler(func=lambda m: self.checkState(m, 'wait_name'))
        def handle_username(message):
            name = self.formatName(message.text)
            if name in self.couches.get('couch_name').to_numpy():
                self.state[message.chat.id] = ['wait_pass', name]
                self.tg_bot.send_message(message.chat.id, 'Введите ваш пароль')
            else:
                self.tg_bot.send_message(message.chat.id, 'Тренера с таким именем не существует')
                self.state.pop(message.chat.id)

        @self.tg_bot.message_handler(func=lambda m: self.checkState(m, 'wait_pass'))
        def handle_password(message):
            if self.checkPassword(self.state[message.chat.id][1], message.text):
                self.tg_bot.send_message(message.chat.id, 'Вы успешно вошли в аккаунт')
                self.saveTgId(message.chat.id, self.state[message.chat.id][1])
                self.state[message.chat.id] = ['logged', self.state[message.chat.id][1]]
            else:
                self.tg_bot.send_message(message.chat.id, 'Введен неверный пароль')
                self.state.pop(message.chat.id)

        @self.tg_bot.message_handler(func=lambda m: self.checkState(m, 'logged'), commands=['logout'])
        def handle_logout(message):
            self.deleteTgId(self.state[message.chat.id][1])
            self.tg_bot.send_message(message.chat.id, 'Вы успешно вышли из аккаунта')
            self.state.pop(message.chat.id)

        @self.tg_bot.message_handler(func=lambda m: self.checkState(m, 'logged'), content_types=CONTENT_TYPES)
        def handle_logged(message):
            self.tg_bot.send_message(message.chat.id, 'Вы уже вошли в аккаунт под именем ' +
                                     self.state[message.chat.id][1] +
                                     '.\r\nЧтобы выйти из аккаунта, напишите "/logout"')

        @self.tg_bot.message_handler(content_types=CONTENT_TYPES)
        def handle_misc(message):
            self.tg_bot.send_message(message.chat.id, 'Ошибка')
            self.state.pop(message.chat.id)

        self.tg_bot.infinity_polling(interval=1)

    def checkState(self, message, state):
        if message.chat.id in self.state.keys():
            return self.state[message.chat.id][0] == state
        return state is None

    def formatName(self, name):
        name = name.title()
        names = self.couches.get('couch_name').to_numpy()
        if name in names:
            return name
        name_set = permutations(name.split())
        names_set = [tuple(set_name.split()) for set_name in names]
        for n in name_set:
            if n in names_set:
                return ' '.join(n)
        return name

    def readCouches(self):
        for couch in self.couches.iterrows():
            if couch[1]['linked_account'] != 'None':
                self.state[int(couch[1]['linked_account'])] = ['logged', couch[1]['couch_name']]

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

    def writeTg(self, user, file_path, receiver):
        receiver_id = receiver['linked_account']
        if receiver_id != 'None':
            user_name = user['name'] + ' ' + user['surname']
            file_path = file_path[:-4] + '_r.csv'
            file_data = pd.read_csv(file_path, delimiter=',')
            file = pd.DataFrame(file_data)
            file.set_index('ind', inplace=True)

            if receiver.index[0] == 'doctor_password':
                file = file.loc[::, 'value']

                results = 'ЧСС: ' + str(int(file['heart_rate'])) + ' уд/мин\r\nЧастота дыхания: ' \
                          + str(int(file['breath_freq'])) + ' вдохов в минуту\r\nВариабельность сердечного ритма: ' \
                          + str(int(file['variability_index'])) + '\r\n'
                alpha_time = int(file['start_time'])
                if alpha_time >= 0:
                    results += 'Время до появления альфа-ритма: ' + str(alpha_time) + 'секунд'
                else:
                    results += 'Альфа ритм не обнаружен'
                text = user_name + ' прошел тестирование.\r\n\r\n<i>Полученные результаты:</i>\r\n' + results
                if user['couch_name'] != 'None':
                    text += '\r\n\r\nТестирование провел тренер ' + user['couch_name']

            elif receiver.index[0] == 'couch_password':
                # recommendation_text = recommendation_text.replace('<br>', '\r\n')
                # recommendation_text = recommendation_text.replace('\r\n\r\n', '\r\n')
                result = file.at['result', 'result']
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

            else:
                text = 'Error'

            self.tg_bot.send_message(receiver_id, text, parse_mode='HTML')
