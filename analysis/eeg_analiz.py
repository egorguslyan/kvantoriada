import matplotlib.pyplot as plt
import numpy as np
from analysis.signal_analysis import *

FILE_PATH = "datasets/1/Semyon/dataEEG_1.txt"
RATE = 200


def open_file_eeg(file_path):
    file = open(file_path, 'r')
    eeg = list(map(int, file.readline().split()))
    for i in range(len(eeg)):
        eeg[i] -= 128
    return eeg


def find_alpha(size, sig, ratio):
    points = []
    freq, x = get_spectrum(0, 70, sig)
    max = 0
    for i in range(len(x)):
        if 8 <= freq[i] <= 14 and x[i] > x[max]:
            max = i
    # sum /= len(x)
    th = ratio * x[max]
    for i in range(len(sig) - size):
        freq, x = get_spectrum(0, 70, sig[i:i + size])

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


def analysis_eeg(eeg):
    properties = {}
    t = get_time(len(eeg), RATE)
    eeg_filtered = filter_low_high_freq(4, 70, eeg, RATE)
    freq, x = get_spectrum(0, 70, eeg_filtered)

    properties["spectrum"] = {
        "freq": freq,
        "x": x
    }

    points = find_alpha(300, eeg_filtered, 2.3)
    points = convert_points_to_time(points, t)

    alpha_segments = []
    start = points[0]
    for i in range(1, len(points)):
        if points[i] - 1 != points[i - 1]:
            alpha_segments.append((points[i - 1] - start, start))
            start = points[i]
    alpha_segments.sort()

    properties["alpha"] = alpha_segments[0][1]
    return properties


if __name__ == "__main__":
    eeg = open_file_eeg(FILE_PATH)
    t = get_time(len(eeg), RATE)

    fig, ax = plt.subplots(4, 1)

    ax[0].plot(t[500:1000], eeg[500:1000])

    eeg_filtered = filter_low_high_freq(4, 70, eeg, RATE)
    ax[0].plot(t[500:1000], eeg_filtered[500:1000])

    ax[1].plot(t, eeg)
    ax[1].plot(t, eeg_filtered)

    freq, x = get_spectrum(0, 100, eeg_filtered)
    ax[2].plot(freq, x)
    freq, x = get_spectrum(0, 100, eeg_filtered[500:800])
    ax[2].plot(freq, x)

    p = find_alpha(300, eeg_filtered, 2.3)
    ax[3].plot(t, eeg_filtered)
    ax[3].scatter(convert_points_to_time(p, t), [130] * len(p))
    print(p)

    p = convert_points_to_time(p, t)
    alpha_segments = []
    start = p[0]
    for i in range(1, len(p)):
        if p[i] - 1 != p[i - 1]:
            alpha_segments.append((p[i - 1] - start, start))
            start = p[i]
    alpha_segments.sort()
    print(alpha_segments[0][1])
    plt.show()
