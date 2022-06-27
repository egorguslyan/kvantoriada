def prediction(ecg, eeg):
    res = 0
    if ecg['heart_rate'] > 70:
        res += 0.209
    print('Heart Rate', ecg['heart_rate'])

    if ecg['breath']['freq'] > 20:
        res += 0.208
    print('Breath',  ecg['breath']['freq'])

    if eeg['spectrum']['start_time'] == -1:
        res += 0.2
    print('alpha',  eeg['spectrum']['start_time'])

    if ecg['variability']['index'] > 150:
        res += 0.2
    print('Variability', ecg['variability']['index'], ecg['variability']['amo'], ecg['variability']['mo'])
    print('RESULT', res)
    return 'Возбуждение' if res > 0.5 else 'Спокоен'

