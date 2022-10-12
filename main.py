import pandas as pd
from telegram.telegram_bot import Bot
from gui import Gui


if __name__ == "__main__":
    # чтение таблиц спортсменов, тренеров и врачей из файлов
    users_data = pd.read_csv('users.csv', delimiter=',')
    users = pd.DataFrame(users_data)
    couches_data = pd.read_csv('couches.csv', delimiter=',', dtype='str')
    couches = pd.DataFrame(couches_data)
    doctors_data = pd.read_csv('doctors.csv', delimiter=',', dtype='str')
    doctors = pd.DataFrame(doctors_data)

    # создание объекта бота и его запуск
    bot_thread = Bot(users, couches, doctors, 'NTc4OTExODUyOTpBQUZoSi1yUEZhSnVqU2xGZXVBMmtpY3lJck5rOVpOOTM0dw==')
    bot_thread.start()
    # создание объекта интерфейса и его запуск
    gui_thread = Gui(users, couches, doctors, bot_thread)
    gui_thread.start()
