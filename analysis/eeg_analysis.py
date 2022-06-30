import matplotlib.pyplot as plt
# import numpy as np
from analysis.signal_analysis import *

FILE_PATH = "datasets/1/Misha/dataEEG_1.txt"
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


def analysis_eeg(eeg):
    properties = {}

    t = get_time(len(eeg), RATE)
    properties['time'] = t
    eeg_filtered = filter_low_high_freq(4, 50, eeg, RATE)
    properties['filtered'] = eeg_filtered.copy()
    # freq, x = get_spectrum(0, 100, eeg_filtered)
    size = 100
    points = find_alpha(size, eeg_filtered, 1.9)
    time_start, amp = find_time_and_amp(eeg_filtered, points, t, size)
    coeff = find_coeff(eeg_filtered, points, amp, size)
    properties["spectrum"] = {
        "amp": "{0:.2f}".format(coeff),
        "start_time": time_start
    }
    return properties


def find_coeff(eeg, points, amp, size):
    prom = []
    for i in points:
        eeg[i] = 1000
    curr = []
    for i in range(len(eeg)):
        if eeg[i] != 1000:
            curr.append(i)
        elif curr:
            prom.append(curr)
            curr = []
    if curr:
        prom.append(curr)
    am = []
    for ee in prom:
        freq, x = get_spectrum(8, 14, ee)
        am.append(sum(x)*size/len(ee))
    ampl = sum(am)/len(am)
    if amp > 0:
        return amp/ampl
    else:
        return -1


def find_time_and_amp(eeg, points, t, size, delay=3):
    time_start = -1
    amp = -1
    if points:
        count = 0
        for i in range(1, len(points)):
            if points[i] == points[i - 1] + 1:
                count += 1
                if count > RATE * delay:
                    time_start = round(convert_points_to_time(points, t)[i - count], 1)
                    break
        amps = []
        for i in points:
            freq, x = get_spectrum(8, 14, eeg[i - size // 2:i + size // 2])
            amps.append(sum(x))
        amp = sum(amps)/len(amps)
    return time_start, amp


def main():
    eeg = open_file_eeg(FILE_PATH)
    t = get_time(len(eeg), RATE)
    eeg_filtered = filter_low_high_freq(4, 70, eeg, RATE)
    freq, x = get_spectrum(0, 100, eeg_filtered)
    p = find_alpha(100, eeg_filtered, 1.9)
    tim_start, amp = find_time_and_amp(eeg_filtered, p, t, 100)
    coeff = find_coeff(eeg_filtered, p, amp, 100)
    print(coeff)

    fig, ax = plt.subplots(3)
    ax[0].plot(t, eeg)
    ax[1].plot(freq, x)
    ax[2].plot(t, eeg_filtered)
    ax[2].scatter(convert_points_to_time(p, t), [amp] * len(p))

    if tim_start > -1:
        print(tim_start, 'секунд до появления альфа-ритма')
    else:
        print('Альфа-ритм не появился')
    plt.show()
    # p = convert_points_to_time(p, t)
    # alpha_segments = []
    # start = p[0]
    # for i in range(1, len(p)):
    #     if p[i] - 1 != p[i - 1]:
    #         alpha_segments.append((p[i - 1] - start, start))
    #         start = p[i]
    # alpha_segments.sort()
    # print(alpha_segments)


if __name__ == "__main__":
    main()
