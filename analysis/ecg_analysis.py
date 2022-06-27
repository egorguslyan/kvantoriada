import matplotlib.pyplot as plt
from analysis.signal_analysis import *

FILE_PATH = "datasets/1/Semyon/datasCalmEKG_1.txt"
RATE = 200
RATIO = 0.3


def find_points_zeros(data, th):
    neg, pos = [], []

    for i in range(1, len(data)):
        if data[i] > th > data[i - 1]:
            pos.append(i)
        elif data[i] < th < data[i - 1]:
            neg.append(i)

    return neg, pos


def median(neg, pos, n):
    if len(neg) == 0:
        if len(pos) == 0:
            return []
        else:
            return [(n + pos[-1]) // 2]
    else:
        if len(pos) == 0:
            return [neg[0] // 2]
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


def find_r_peak(n, m, ratio, data):
    g = convert_signal(n, m, data)

    th = ratio * max(g)
    neg, pos = find_points_zeros(g, th)

    r = median(neg, pos, len(g))

    return g, np.unique(r)


def calibrate_r_peak(r, data, size):
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


def find_breath_freq(data):
    th = min(data) + (max(data) - min(data)) * 0.3
    points = []
    ind = 0
    for i in range(len(data)):
        if data[i] < data[ind] and data[i] < th:
            ind = i
        elif data[i] >= th > data[i - 1]:
            points.append(ind)
        elif data[i] > th:
            ind = i
    return points


def variability(var):
    max_value = max(var)
    min_value = min(var)
    amplitude = max_value - min_value

    step = 50

    hist = [0] * (int(2000 / step))
    for e in var:
        hist[int(e / step)] += 1

    amo = max(hist)
    mo = step * (hist.index(amo))
    amo = amo * 100 / len(var)
    if mo * amplitude != 0:
        index_baevskogo = amo / (2 * mo * amplitude / 10 ** 6)
    else:
        index_baevskogo = 0

    return {
        'histogram': hist,
        'min': int(min_value),
        'max': int(max_value),
        'amplitude': int(amplitude),
        'amo': amo,
        'mo': mo,
        'index': int(index_baevskogo)
    }


def analysis_ecg(ecg):
    properties = {}
    t = get_time(len(ecg), RATE)
    properties['time'] = t
    ecg_filtered = filter_low_high_freq(0.2, 30, ecg, RATE)
    # freq, x = get_spectrum(0, 7, ecg_filtered)

    g, r_old = find_r_peak(15, 8, RATIO, ecg_filtered)
    var = [r_old[i] - r_old[i - 1] for i in range(1, len(r_old))]
    if len(var) > 0:
        r = calibrate_r_peak(r_old, ecg, max(var) // 2)

        r_new = convert_points_to_time(r, t)

        properties["heart_rate"] = int(len(r_new) * (60 / t[-1]))
        var = [(r_new[i] - r_new[i - 1]) * 1000 for i in range(1, len(r_new))]

        properties["variability"] = variability(var)

        breath = [g[i] for i in r_old]
        max_breath = max(breath)
        min_breath = min(breath)
        ampl_breath = max_breath - min_breath

        freq_breath = len(find_breath_freq(breath)) * 60 / t[-1]
        properties["breath"] = {
            "max": int(max_breath),
            "min": int(min_breath),
            "amplitude": int(ampl_breath),
            "freq": int(freq_breath)
        }
    else:
        properties["heart_rate"] = 0
        properties["variability"] = variability([0] * 2)
        properties["breath"] = {
            "max": 0,
            "min": 0,
            "amplitude": 0,
            "freq": 0
        }

    return properties


def main():
    ecg = open_file(FILE_PATH)

    t = get_time(len(ecg), RATE)

    fig, ax = plt.subplots(7, 1)
    ax[0].plot(t[:250], ecg[:250])

    ecg_filtered = filter_low_high_freq(0.2, 30, ecg, RATE)
    ax[0].plot(t[:250], ecg_filtered[:250])

    freq, x = get_spectrum(0, 7, ecg_filtered)
    ax[1].plot(freq, x)

    g, r_old = find_r_peak(15, 8, RATIO, ecg_filtered)
    var = [r_old[i] - r_old[i - 1] for i in range(1, len(r_old))]
    r = calibrate_r_peak(r_old, ecg, max(var) // 2)

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
    points = find_breath_freq(breath)
    print(points)
    ax[5].plot(g)
    ax[5].plot(r_old, breath)
    ax[5].plot([0, len(g)], [max_breath] * 2)
    ax[5].plot([0, len(g)], [min_breath] * 2)

    ax[6].plot(breath)
    ax[6].scatter(points, [10] * len(points))

    plt.show()


if __name__ == "__main__":
    main()
