import serial
import matplotlib.pyplot as plt
from collections import deque

size = 32
time = 15
size_package = 200 * time

my_serial = serial.Serial('COM6', 38400, timeout=0.1)
file = open('datasets/1/Misha/datasRelaxEKG_1.txt', 'w')

y = deque([128]*512)
x = deque([128]*512)

plt.ion()
fig, ax = plt.subplots(2)
ax[0].set_xlim(0, 512)
ax[1].set_xlim(0, 512)
ax[0].set_ylim(0, 255)
ax[1].set_ylim(0, 255)
line1, = ax[0].plot(range(512), y)
line2, = ax[1].plot(range(512), x)

try:
    a = int.from_bytes(my_serial.read(), 'little')
    while a != 255:
        a = int.from_bytes(my_serial.read(), 'little')

    for _ in range(size_package // size):
        v = [0] * size
        i = 0
        while i < size:
            if my_serial.in_waiting > 0:
                v[i] = int.from_bytes(my_serial.read(), 'little')
                i += 1

        if len(y) < 512:
            y.extend(v)
        else:
            for j in range(size):
                y.popleft()
            y.extend(v)

        line1.set_ydata(y)

        fig.canvas.draw()
        fig.canvas.flush_events()
        file.write(' '.join(map(str, v)))
        file.write(' ')

    plt.close()
    file.close()
    my_serial.close()
except KeyboardInterrupt:
    plt.close()
    file.close()
    my_serial.close()
    print('Bye')