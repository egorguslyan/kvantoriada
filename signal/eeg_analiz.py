import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

FILE_PATH = "datasets/1/Semyon/dataEEG_1.txt"
RATE = 200


def butterBandPassFilter(lowcut, highcut, samplerate, order):
    semiSampleRate = samplerate*0.5
    low = lowcut / semiSampleRate
    high = highcut / semiSampleRate
    b,a = signal.butter(order,[low,high],btype='bandpass')
    return b,a


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


def open_file_eeg(file_path):
    file = open(file_path, 'r')
    eeg = list(map(int, file.readline().split()))
    for i in range(len(eeg)):
        eeg[i] -= 128
    return eeg


def filter_lowhigh_freq(low, high, x):
    b,a = butterBandPassFilter(low, high, RATE, order=4)
    x = signal.lfilter(b, a, x)
    return x


def find_alpha(size, sig, ratio):
    points = []
    freq, x = fft(0, 70, sig)
    max = 0
    for i in range(len(x)):
        if 8 <= freq[i] <= 14 and x[i] > x[max]:
            max = i
    #sum /= len(x)
    th = ratio * x[max]
    for i in range(len(sig) - size):
        freq, x = fft(0, 70, sig[i:i + size])

        ind = 0
        for j in range(len(x)):
            if x[j] > x[ind]:
                ind = j

        if 8 <= freq[ind] <= 14:
            max = 0
            for j in range(len(x)):
                if 8 <= freq[j] <= 14 and x[j] > x[max]:
                    max = j

            if x[max] > th:
                points.append(i)

    return points


def convert_points_to_time(p, t):
    return [t[i] for i in p]


eeg = open_file_eeg(FILE_PATH)
t = np.linspace(0, len(eeg) / RATE, len(eeg))

fig, ax = plt.subplots(4, 1)

ax[0].plot(t[500:1000], eeg[500:1000])

eeg_filt = filter_lowhigh_freq(4, 70, eeg)
ax[0].plot(t[500:1000], eeg_filt[500:1000])

ax[1].plot(t, eeg)
ax[1].plot(t, eeg_filt)

freq, x = fft(0, 100, eeg_filt)
ax[2].plot(freq, x)
freq, x = fft(0, 100, eeg_filt[500:800])
ax[2].plot(freq, x)

p = find_alpha(300, eeg_filt, 2.3);
ax[3].plot(t, eeg_filt)
ax[3].scatter(convert_points_to_time(p, t), [130] * len(p))
print(p)
plt.show()