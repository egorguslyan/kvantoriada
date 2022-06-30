def prediction(ecg, eeg):
    res = 0
    status = {}
    if ecg['heart_rate'] > 70:
        res += 0.209
        status['heart_rate'] = 'excited'
    else:
        status['heart_rate'] = 'good'
    print('Heart Rate', ecg['heart_rate'])

    status['breath'] = {}
    if ecg['breath']['freq'] > 20:
        res += 0.208
        status['breath']['freq'] = 'excited'
    else:
        status['breath']['freq'] = 'good'
    print('Breath',  ecg['breath']['freq'])

    status['spectrum'] = {}
    if eeg['spectrum']['start_time'] == -1:
        res += 0.2
        status['spectrum']['start_time'] = 'excited'
    else:
        status['spectrum']['start_time'] = 'good'
    print('alpha',  eeg['spectrum']['start_time'])

    status['variability'] = {}
    if ecg['variability']['index'] > 100:
        res += 0.2
        status['variability']['index'] = 'excited'
    else:
        status['variability']['index'] = 'good'
    print('Variability', ecg['variability']['index'], ecg['variability']['amo'], ecg['variability']['mo'])

    print('RESULT', res)
    status['result'] = {'color': 'excited'} if res > 0.5 else {'color': 'good'}

    return status
