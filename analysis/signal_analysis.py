import numpy as np
from scipy import signal
import os


def open_file(file_path):
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
    b, a = butter_band_pass_filter(low, high, rate, order=4)
    data_filtered = signal.lfilter(b, a, data)
    return data_filtered


def get_spectrum(low, high, data):
    freq = np.fft.rfftfreq(len(data), 0.005)
    x = np.abs(np.fft.rfft(data) / len(data))

    freq_new = []
    x_new = []
    for i in range(len(x)):
        if low < freq[i] < high:
            x_new.append(x[i])
            freq_new.append(freq[i])

    return freq_new, x_new


def get_time(length, rate):
    return np.linspace(0, length / rate, length)


def convert_points_to_time(points, time):
    return [time[i] for i in points]
