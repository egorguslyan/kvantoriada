import matplotlib.pyplot as plt
from collections import deque

file1 = open('dataCalmEKG3.txt')
file2 = open('dataCalmEKG3.txt')

size = 16

y1 = deque([128] * (size*32))
x1 = deque([128] * (size*32))
y2 = deque([128] * (size*32))
x2 = deque([128] * (size*32))
plt.ion()
fig, ax = plt.subplots(2, 2)
for axe in ax.flat:
    axe.set_xlim(0, (size*32))
    axe.set_ylim(0, 255)
line11, = ax[0, 0].plot(range((size*32)), y1)
line21, = ax[0, 1].plot(range((size*32)), x1)
line12, = ax[1, 0].plot(range((size*32)), y2)
line22, = ax[1, 1].plot(range((size*32)), x2)


def unpack_str(sf):
    sf = sf[:-1]
    ef, gf = sf.split(',')
    # ef = sf
    # gf = ''
    ekf = ef.split()
    gsf = gf.split()
    ekgf = list(map(int, ekf))
    gsrf = list(map(int, gsf))
    while len(gsrf) < size:
        gsrf.append(128)
    while len(ekgf) < size:
        ekgf.append(128)
    return ekgf, gsrf


s1 = file1.readline()
s2 = file2.readline()
try:
    while s1 != '' and s2 != '':
        ekg1, gsr1 = unpack_str(s1)
        ekg2, gsr2 = unpack_str(s2)
        for i in range(size):
            y1.popleft()
            x1.popleft()
            y2.popleft()
            x2.popleft()
        y1.extend(ekg1)
        x1.extend(gsr1)
        y2.extend(ekg2)
        x2.extend(gsr2)
        line11.set_ydata(y1)
        line21.set_ydata(x1)
        line12.set_ydata(y2)
        line22.set_ydata(x2)
        fig.canvas.draw()
        fig.canvas.flush_events()
        s1 = file1.readline()
        s2 = file2.readline()

except KeyboardInterrupt:
    plt.close()
    file1.close()
    file2.close()
    print('Bye')
finally:
    file1.close()
    file2.close()
    plt.close()
