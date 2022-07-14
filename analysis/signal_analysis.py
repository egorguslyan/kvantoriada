import numpy as np
from scipy import signal
import os
import pandas as pd


def open_csv_file(file_path):
    '''
    чтение данных из .csv файла
    :param file_path: файл
    :return: таблица
    '''
    if not os.path.exists(file_path):
        return {
            'ecg': [[0] * 512, 3, 0],
            'eeg': [[0] * 512, 3, 0],
            'gsr': [[0] * 512, 3, 0]
        }
    data = pd.read_csv(file_path, delimiter=',')
    signals = data.iloc[0]
    ecg = list(map(lambda x: int(x) - 128, signals['ecg'].split()))
    eeg = list(map(lambda x: int(x) - 128, signals['eeg'].split()))
    gsr = list(map(lambda x: int(x) - 128, signals['gsr'].split()))

    times = data.iloc[1]
    time_ecg = int(times['ecg'])
    time_eeg = int(times['eeg'])
    time_gsr = int(times['gsr'])

    enables = data.iloc[2]
    enable_ecg = int(enables['ecg'])
    enable_eeg = int(enables['eeg'])
    enable_gsr = int(enables['gsr'])
    return {
        'ecg': [ecg, time_ecg, enable_ecg],
        'eeg': [eeg, time_eeg, enable_eeg],
        'gsr': [gsr, time_gsr, enable_gsr]
    }


def open_file(file_path):
    '''
    чтение из файла
    :param file_path: файл
    :return: сигнал
    '''
    if not os.path.exists(file_path):
        return [0] * 512
    with open(file_path, 'r') as file:
        data = list(map(lambda a: int(a) - 128, file.readline().split()))
        return data


def butter_band_pass_filter(lowcut, highcut, samplerate, order):
    semi_sample_rate = samplerate * 0.5
    low = lowcut / semi_sample_rate
    high = highcut / semi_sample_rate
    b, a = signal.butter(order, [low, high], btype='bandpass')
    return b, a


def butter_band_stop_filter(lowcut, highcut, samplerate, order):
    semi_sample_rate = samplerate * 0.5
    low = lowcut / semi_sample_rate
    high = highcut / semi_sample_rate
    b, a = signal.butter(order, [low, high], btype='bandstop')
    return b, a


def filter_low_high_freq(low, high, data, rate):
    '''
    фильтр сигнала от низких и высоких частот
    :param low: нижний порог
    :param high: верхний порог
    :param data: сигнал
    :param rate: частота
    :return: отфильтрованный сигнал
    '''
    b, a = butter_band_pass_filter(low, high, rate, order=4)
    data_filtered = signal.lfilter(b, a, data)
    return data_filtered


def get_spectrum(low, high, data, rate):
    '''
    нахождений спектра
    :param low: нижний порог
    :param high: верхний порог
    :param data: сигнал
    :param rate: частота
    :return: спектр
    '''
    freq = np.fft.rfftfreq(len(data), 1 / rate)
    x = np.abs(np.fft.rfft(data) / len(data))

    freq_new = []
    x_new = []
    for i in range(len(x)):
        if low < freq[i] < high:
            x_new.append(x[i])
            freq_new.append(freq[i])

    return freq_new, x_new


def get_time(length, rate):
    '''
    получение времени длительности сигнала
    :param length: длинна сигнала
    :param rate: частота
    :return: время
    '''
    return np.linspace(0, length / rate, length)


def convert_points_to_time(points, time):
    '''
    преобразование точек в точки на временном отрезке
    :param points: точки
    :param time: время
    :return:
    '''
    return [time[i] for i in points]
