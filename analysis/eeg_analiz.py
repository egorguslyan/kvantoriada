import matplotlib.pyplot as plt
# import numpy as np
from signal_analysis import *

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
    freq, x = get_spectrum(4, 70, sig)
    max_amp = max(x)
    freq, x = get_spectrum(8, 14, sig)
    if max(x) == max_amp:
        th = ratio * max_amp
        for i in range(len(sig) - size):
            freq, x = get_spectrum(8, 14, sig[i:i + size])
            if max(x) > th:
                points.append(i+size//2)
    return points


def analysis_eeg(eeg):  # do not use
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


def find_time_and_amp(eeg, points, t, size):
    amps = []
    if p:
        time_start = round(min(convert_points_to_time(points, t)), 1)
        for i in points:
            freq, x = get_spectrum(8, 14, eeg[i - size // 2:i + size // 2])
            amps.append(sum(x)+30)
    else:
        time_start = -1
    return time_start, amps


if __name__ == "__main__":
    eeg = open_file_eeg(FILE_PATH)
    t = get_time(len(eeg), RATE)
    eeg_filtered = filter_low_high_freq(4, 70, eeg, RATE)
    freq, x = get_spectrum(0, 100, eeg_filtered)
    p = find_alpha(100, eeg_filtered, 1.9)
    tim_start, amps = find_time_and_amp(eeg_filtered, p, t, 100)

    fig, ax = plt.subplots(3)
    ax[0].plot(t, eeg)
    # ax[0].plot(t, eeg_filtered)
    ax[1].plot(freq, x)
    # freq, x = get_spectrum(0, 100, eeg_filtered[500:800])
    # ax[1].plot(freq, x)
    ax[2].plot(t, eeg_filtered)
    ax[2].scatter(convert_points_to_time(p, t), amps)
    plt.show()

    if tim_start > -1:
        print(tim_start, 'секунд до появления альфа-ритма')
    else:
        print('Альфа-ритм не появился')

    # p = convert_points_to_time(p, t)
    # alpha_segments = []
    # start = p[0]
    # for i in range(1, len(p)):
    #     if p[i] - 1 != p[i - 1]:
    #         alpha_segments.append((p[i - 1] - start, start))
    #         start = p[i]
    # alpha_segments.sort()
    # print(alpha_segments)
