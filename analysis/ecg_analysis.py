import matplotlib.pyplot as plt
from analysis.signal_analysis import *

FILE_PATH = "datasets/1_)7"
RATE = 200
RATIO = 0.3


def find_points_zeros(data, th):
    '''
    нахождение пороговых точек
    :param data: график
    :param th: порог
    :return: лист точек
    '''
    neg, pos = [], []

    for i in range(1, len(data)):
        if data[i] > th > data[i - 1]:
            pos.append(i)
        elif data[i] < th < data[i - 1]:
            neg.append(i)

    return neg, pos


def median(neg, pos, n):
    '''
    нахождение середин отрезков
    :param neg: лист точек
    :param pos: лист точек
    :param n: длина графика
    :return: лист точек
    '''
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
    '''
    получение вспомогательного графика
    :param n:
    :param m:
    :param data: график ЭКГ
    :return: вспомогательный график
    '''
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
    '''
    нахождение R-зубцов
    :param n:
    :param m:
    :param ratio: порог
    :param data: сигнал ЭКГ
    :return:
    '''
    g = convert_signal(n, m, data)

    th = ratio * max(g)
    neg, pos = find_points_zeros(g, th)

    r = median(neg, pos, len(g))

    return g, np.unique(r)


def calibrate_r_peak(r, data, size):
    '''
    соотнесение найденных R-зубцов с реальными
    :param r: лист R-зубцов
    :param data: ЭКГ
    :param size: окошко поиска
    :return:
    '''
    res = []
    for i in r:
        ind = i
        for k in range(-size // 2, size // 2):
            if 0 <= i + k < len(data) and data[i + k] > data[ind]:
                ind = i + k
        res.append(ind)
    return np.unique(res)


def distribution(a, step):
    '''
    распределение RR
    :param a:
    :param step:
    :return: график
    '''
    x = [0] * (int(max(a)) // step + 1)
    for e in a:
        x[int(e) // step] += 1
    return list(range(0, len(x) * step, step)), x


def find_breath_freq(data):
    '''
    нахождение частоты дыхания
    :param data: график дыхания
    :return: частота
    '''
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
    '''
    анализ вариабельности сердечного ритма
    :param var:
    :return:
    '''
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


def analysis_ecg(data):
    '''
    анализ ЭКГ
    :param data: ЭКГ
    :return: свойства
    '''
    ecg = data[0]
    time = data[1]
    enable = data[2]
    properties = dict()
    properties['time'] = list(range(len(ecg)))
    properties["heart_rate"] = 0
    properties["diff_heart_rate"] = '-'
    properties["variability"] = variability([0] * 2)
    properties["breath"] = {
        "max": 0,
        "min": 0,
        "amplitude": 0,
        "freq": 0
    }
    if enable == 1:
        try:
            RATE = len(ecg) // time
            t = get_time(len(ecg), RATE)
            properties['time'] = t
            ecg_filtered = filter_low_high_freq(0.2, 30, ecg, RATE)
            # freq, x = get_spectrum(0, 7, ecg_filtered)

            g, r_old = find_r_peak(15, 8, RATIO, ecg_filtered)
            var = [r_old[i] - r_old[i - 1] for i in range(1, len(r_old))]
            r = calibrate_r_peak(r_old, ecg, max(var) // 2)

            r_new = convert_points_to_time(r, t)

            # properties["heart_rate"] = int(len(r_new) * (60 / t[-1]))
            var = [(r_new[i] - r_new[i - 1]) * 1000 for i in range(1, len(r_new))]

            properties["variability"] = variability(var)
            properties['heart_rate'] = int(60 * 1000 / properties['variability']['mo'])

            if t[-1] >= 60:
                begin_heart_rate = int(60 * 1000 / variability(var[:20])['mo'])
                end_heart_rate = int(60 * 1000 / variability(var[-20:-1])['mo'])
                properties["diff_heart_rate"] = str(begin_heart_rate - end_heart_rate)

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
        except:
            pass

    return properties


def main():
    ecg = open_file(FILE_PATH)

    t = get_time(len(ecg), RATE)

    fig, ax = plt.subplots(7, 1)
    ax[0].plot(t[:250], ecg[:250])

    ecg_filtered = filter_low_high_freq(0.2, 30, ecg, RATE)
    ax[0].plot(t[:250], ecg_filtered[:250])

    freq, x = get_spectrum(0, 7, ecg_filtered, RATE)
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
