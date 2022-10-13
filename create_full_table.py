import pandas as pd
import datetime
import re
import os

users_data = pd.read_csv('users.csv', delimiter=',')
users = pd.DataFrame(users_data)

general = pd.DataFrame([], columns=['id', 'date', 'age', 'heart_rate', 'variability', 'breath_freq', 'alpha', 'result'])

for i in range(len(users)):
    user = users.iloc[i]

    time_format = '%d.%m.%Y'
    birthday = datetime.datetime.strptime(user['birthday'], time_format)
    now = datetime.datetime.now()
    age = now.year - birthday.year
    if now.month < birthday.month:
        age -= 1
    elif now.month == birthday.month and now.day < birthday.day:
        age -= 1

    files = os.listdir(user['dir_path'])
    for file in files:
        if re.search(r'\d\d.\d\d.\d{4} \d\d-\d\d-\d\d_r', file):
            data = pd.read_csv(os.path.join(user['dir_path'], file), delimiter=',').set_index('ind')
            t = {
                'id': user['dir_path'][6:],
                'date': file[:-6],
                'age': age,
                'heart_rate': int(data.at['heart_rate', 'value']),
                'variability': int(data.at['variability_index', 'value']),
                'breath_freq': int(data.at['breath_freq', 'value']),
                'alpha': float(data.at['start_time', 'value']),
                'result': int(data.at['result', 'result']) - 1
            }

            general = general.append(t, ignore_index=True)
general.to_csv('general.csv', index=False)
print(general)
