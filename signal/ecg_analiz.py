import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

FILE_PATH = "datasets/31/dataCalmEKG_2.txt"
RATE = 200
RATIO = 0.3


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


def open_file(file_path):
    file = open(file_path, 'r')
    data = list(map(lambda a: int(a) - 128, file.readline().split()))
    return data


def filter_low_high_freq(low, high, data):
    b, a = butter_band_pass_filter(low, high, RATE, order=4)
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


def find_points_zeros(data, th):
    neg, pos = [], []

    for i in range(1, len(data)):
        if data[i] > th > data[i - 1]:
            pos.append(i)
        elif data[i] < th < data[i - 1]:
            neg.append(i)

    return neg, pos


def median(neg, pos, n):
    p = []
    start_neg = 0
    if neg[0] < pos[0]:
        p.append(neg[0] // 2)
        start_neg = 1

    for i in range(min(len(neg) - start_neg, len(pos))):
        p.append((neg[i + start_neg] + pos[i]) // 2)

    if len(neg) - start_neg != len(pos):
        p.append((n + pos[-1]) // 2)

    return p


def convert_signal(n, m, data):
    g1 = [5] * len(data)

    for i in range(len(g1)):
        for j in range(n):
            g1[i] += abs(data[i - j] - data[i - j - 1]) ** 2 * (n - j)

    g = [0] * len(g1)
    for n in range(len(g)):
        for i in range(m):
            g[n] += g1[n - i] / m

    return g


def find_r(n, m, ratio, data):
    g = convert_signal(n, m, data)

    th = ratio * max(g)
    neg, pos = find_points_zeros(g, th)

    r = median(neg, pos, len(g))

    return g, np.unique(r)


def convert_points_to_time(points, time):
    return [time[i] for i in points]


def calibrate_r(r, data, size):
    res = []
    for i in r:
        ind = i
        for k in range(-size // 2, size // 2):
            if 0 <= i + k < len(data) and data[i + k] > data[ind]:
                ind = i + k
        res.append(ind)
    return np.unique(res)


def distribution(a, step):
    x = [0] * (int(max(a)) // step + 1)
    for e in a:
        x[int(e) // step] += 1
    return list(range(0, len(x) * step, step)), x

def get_time(length, rate):
    return np.linspace(0, length / rate, length)


def analysis_ecg(ecg):
    properties = {}

    ecg_filtered = filter_low_high_freq(0.2, 30, ecg)
    freq, x = get_spectrum(0, 7, ecg_filtered)

    g, r_old = find_r(15, 8, RATIO, ecg_filtered)
    var = [r_old[i] - r_old[i - 1] for i in range(1, len(r_old))]
    r = calibrate_r(r_old, ecg, max(var) // 2)

    r_new = convert_points_to_time(r, t)

    properties["heart rate"] = int(len(r_new) * (60 / t[-1]))
    var = [(r_new[i] - r_new[i - 1]) * 1000 for i in range(1, len(r_new))]

    properties["variability"] = {
        "min": min(var),
        "max": max(var),
    }

    breath = [g[i] for i in r_old]
    max_breath = max(breath)
    min_breath = min(breath)
    ampl_breath = max_breath - min_breath

    properties["breath"] = {
        "max": max_breath,
        "min": min_breath,
        "amplitude": ampl_breath
    }

    return properties


if __name__ == "__main__":
    ecg = open_file(FILE_PATH)

    t = get_time(len(ecg), RATE)

    fig, ax = plt.subplots(6, 1)
    ax[0].plot(t[:250], ecg[:250])

    ecg_filtered = filter_low_high_freq(0.2, 30, ecg)
    ax[0].plot(t[:250], ecg_filtered[:250])

    freq, x = get_spectrum(0, 7, ecg_filtered)
    ax[1].plot(freq, x)

    g, r_old = find_r(15, 8, RATIO, ecg_filtered)
    var = [r_old[i] - r_old[i - 1] for i in range(1, len(r_old))]
    r = calibrate_r(r_old, ecg, max(var) // 2)

    r_new = convert_points_to_time(r, t)

    ax[2].plot(t, ecg)
    ax[2].scatter(r_new, [10] * len(r))

    ax[3].plot(t, g)
    ax[3].scatter(r_new, [max(g) * RATIO] * len(r_new))

    print("ЧСС : ", int(len(r_new) * (60 / t[-1])))

    var = [(r_new[i] - r_new[i - 1]) * 1000 for i in range(1, len(r_new))]

    print("Вариабельность (макс, мин, разность) : ", max(var), min(var), max(var) - min(var))

    step = 10
    x, y = distribution([abs(var[i] - var[i - 1]) for i in range(1, len(var))], step)
    ax[4].scatter(x, y)

    breath = [g[i] for i in r_old]
    max_breath = max(breath)
    min_breath = min(breath)
    ampl_breath = max_breath - min_breath

    ax[5].plot(g)
    ax[5].plot(r_old, breath)
    ax[5].plot([0, len(g)], [max_breath] * 2)
    ax[5].plot([0, len(g)], [min_breath] * 2)

    plt.show()
