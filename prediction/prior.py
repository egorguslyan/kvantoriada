def prior_analysis(ecg, eeg):
    res = 0.5
    status = {}

    if ecg['heart_rate'] < 70:
        status['heart_rate'] = 0
        res -= 0.125
    elif ecg['heart_rate'] < 90:
        status['heart_rate'] = 1
    else:
        status['heart_rate'] = 2
        res += 0.125
    print('Heart Rate', ecg['heart_rate'])

    status['breath'] = {}
    if ecg['breath']['freq'] < 10:
        status['breath']['freq'] = 0
        res -= 0.125
    elif ecg['breath']['freq'] < 20:
        status['breath']['freq'] = 1
    else:
        status['breath']['freq'] = 2
        res += 0.125
    print('Breath',  ecg['breath']['freq'])

    status['spectrum'] = {}
    if eeg['spectrum']['start_time'] == -1 or eeg['spectrum']['start_time'] > 1.5:
        status['spectrum']['start_time'] = 2
        res += 0.125
    elif eeg['spectrum']['start_time'] < 0.7:
        status['spectrum']['start_time'] = 0
        res -= 0.25
    else:
        status['spectrum']['start_time'] = 1
    print('alpha',  eeg['spectrum']['start_time'])

    # if eeg['spectrum']['amplitude'] < 4:
    #     status['spectrum']['amplitude'] = 2
    #     res += 0.1
    # elif eeg['spectrum']['amplitude'] < 6:
    #     status['spectrum']['amplitude'] = 1
    # else:
    #     status['spectrum']['amplitude'] = 0
    #     res -= 0.1
    # print(eeg['spectrum']['amplitude'])

    status['variability'] = {}
    if ecg['variability']['index'] < 50:
        status['variability']['index'] = 0
        res -= 0.125
    elif ecg['variability']['index'] < 150:
        status['variability']['index'] = 1
    else:
        status['variability']['index'] = 2
        res += 0.125

    print('Variability', ecg['variability']['index'], ecg['variability']['amo'], ecg['variability']['mo'])

    print('RESULT', res)
    if res <= 0.2:
        status['result'] = 0
    elif res < 0.8:
        status['result'] = 1
    else:
        status['result'] = 2

    return status
