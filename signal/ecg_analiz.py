import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

FILE_PATH = "datasets/31/dataCalmEKG_2.txt"
RATE = 200
RATIO = 0.3


def butterBandPassFilter(lowcut, highcut, samplerate, order):
    semiSampleRate = samplerate * 0.5
    low = lowcut / semiSampleRate
    high = highcut / semiSampleRate
    b, a = signal.butter(order, [low, high], btype='bandpass')
    return b, a


def butterBandStopFilter(lowcut, highcut, samplerate, order):
    semiSampleRate = samplerate * 0.5
    low = lowcut / semiSampleRate
    high = highcut / semiSampleRate
    b, a = signal.butter(order, [low, high], btype='bandstop')
    return b, a


def open_file_ecg(file_path):
    file = open(file_path, 'r')
    ecg = list(map(int, file.readline().split()))
    ecg = ecg[250:]
    for i in range(len(ecg)):
        ecg[i] -= 128
    return ecg


def filter_lowhigh_freq(low, high, x):
    b, a = butterBandPassFilter(low, high, RATE, order=4)
    x = signal.lfilter(b, a, x)
    return x


def filter_kalman(k, x):
    x = x.copy()
    for i in range(len(x)):
        x[i] = x[i - 1] * (1 - k) + x[i] * k
    return x


def fft(low, high, x):
    freq = np.fft.rfftfreq(len(x), 0.005)
    x = np.abs(np.fft.rfft(x) / len(x))

    freq_new = []
    x_new = []
    for i in range(len(x)):
        if low < freq[i] < high:
            x_new.append(x[i])
            freq_new.append(freq[i])

    return freq_new, x_new


def find_points_th(g, size, th):
    p = []
    for i in range(0, len(g) - size + 1, size):
        t = i
        for j in range(size):
            if i + j < len(g) and g[j + i] > th and g[j + i] > g[t]:
                t = j + i
        if g[t] > th:
            ind = t
            for k in range(-size // 2, size // 2):
                if 0 <= t + k < len(x) and x[t + k] > x[ind]:
                    ind = t + k
            p.append(ind)
    return p


def find_points_zeros(x, th):
    neg, pos = [], []

    for i in range(1, len(x)):
        if x[i] - th > 0 and x[i - 1] - th < 0:
            pos.append(i)
        elif x[i] - th < 0 and x[i - 1] - th > 0:
            neg.append(i)

    return neg, pos


def mediana(neg, pos, n):
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


def convert_signal(N, M, x):
    g1 = [5] * len(x)

    for i in range(len(g1)):
        for j in range(N):
            g1[i] += abs(x[i - j] - x[i - j - 1]) ** 2 * (N - j)

    g = [0] * len(g1)
    for n in range(len(g)):
        for i in range(M):
            g[n] += g1[n - i] / M

    return g


def find_r(N, M, ratio, x):
    g = convert_signal(N, M, x)

    th = ratio * max(g)
    neg, pos = find_points_zeros(g, th)

    r = mediana(neg, pos, len(g))

    return g, np.unique(r)


def convert_points_to_time(p, t):
    return [t[i] for i in p]


def calibrate_r(r, x, size):
    res = []
    for i in r:
        ind = i
        for k in range(-size // 2, size // 2):
            if 0 <= i + k < len(x) and x[i + k] > x[ind]:
                ind = i + k
        res.append(ind)
    return np.unique(res)


def distribution(a, step):
    x = [0] * (int(max(a)) // step + 1)
    for e in a:
        x[int(e) // step] += 1
    return list(range(0, len(x) * step, step)), x


# еще определение дыхания

ecg = open_file_ecg(FILE_PATH)

t = np.linspace(0, len(ecg) / RATE, len(ecg))

fig, ax = plt.subplots(6, 1)
ax[0].plot(t[:250], ecg[:250])

ecg_filt = filter_lowhigh_freq(0.2, 30, ecg)
ax[0].plot(t[:250], ecg_filt[:250])

ecg_kalman = filter_kalman(0.3, ecg_filt)
ax[1].plot(t[:250], ecg_filt[:250])
ax[1].plot(t[:250], ecg_kalman[:250])

freq, x = fft(0, 7, ecg_filt)
ax[2].plot(freq, x)

g, r = find_r(15, 8, RATIO, ecg_filt)
var = [r[i] - r[i - 1] for i in range(1, len(r))]
r = calibrate_r(r, ecg, max(var) // 2)

r = convert_points_to_time(r, t)

ax[3].plot(t, ecg)
ax[3].scatter(r, [10] * len(r))

ax[4].plot(t, g)
ax[4].scatter(r, [max(g) * RATIO] * len(r))

print(len(r))
print("ЧСС : ", int(len(r) * (60 / t[-1])))

var = [(r[i] - r[i - 1]) * 1000 for i in range(1, len(r))]

print("Вариабельность (макс, мин, разность) : ", max(var), min(var), max(var) - min(var))

step = 10
print([abs(var[i] - var[i - 1]) for i in range(1, len(var))])
x, y = distribution([abs(var[i] - var[i - 1]) for i in range(1, len(var))], step)
ax[5].scatter(x, y)

plt.show()