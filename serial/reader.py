import matplotlib.pyplot as plt
from collections import deque

file = open('dataCalmTestGsr2.txt')
y = deque([128] * 512)
x = deque([128] * 512)
size = 16
plt.ion()
fig, ax = plt.subplots(2)
ax[0].set_xlim(0, 512)
ax[1].set_xlim(0, 512)
ax[0].set_ylim(0, 255)
ax[1].set_ylim(0, 255)
line1, = ax[0].plot(range(512), y)
line2, = ax[1].plot(range(512), x)

s = file.readline()
try:
    while s != '':
        s = s[:-1]
        e, g = s.split(',')
        ek = e.split()
        gs = g.split()
        ekg = list(map(int, ek))
        gsr = list(map(int, gs))
        while len(gsr) < size:
            gsr.append(128)
        while len(ekg) < size:
            ekg.append(128)
        for i in range(size):
            y.popleft()
            x.popleft()
        y.extend(ekg)
        x.extend(gsr)
        line1.set_ydata(y)
        line2.set_ydata(x)
        fig.canvas.draw()
        fig.canvas.flush_events()
        s = file.readline()
except KeyboardInterrupt:
    plt.close()
    file.close()
    print('Bye')
finally:
    file.close()
    plt.close()