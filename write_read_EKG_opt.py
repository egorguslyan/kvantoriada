import serial
import matplotlib.pyplot as plt
from collections import deque

size = 16
plt.ion()

my_serial = serial.Serial('COM6', 38400, timeout=0.1)
file = open('dataCalmTestGsr.txt', 'a')

y = deque([128]*512)
x = deque([128]*512)
fig, ax = plt.subplots(2)
ax[0].set_xlim(0, 512)
ax[1].set_xlim(0, 512)
ax[0].set_ylim(0, 255)
ax[1].set_ylim(0, 255)
line1, = ax[0].plot(range(512), y)
line2, = ax[1].plot(range(512), x)

try:
    while True:
        a = int.from_bytes(my_serial.read(), 'little')
        if a == 255:
            v = [0] * size
            i = 0
            while i < size:
                if my_serial.in_waiting > 0:
                    v[i] = int.from_bytes(my_serial.read(), 'little')
                    i += 1
            z = [0] * size
            i = 0
            while i < size:
                if my_serial.in_waiting > 0:
                    z[i] = int.from_bytes(my_serial.read(), 'little')
                    i += 1
            if len(y) < 512:
                y.extend(v)
            else:
                for j in range(size):
                    y.popleft()
                y.extend(v)
            if len(x) < 512:
                x.extend(z)
            else:
                for j in range(size):
                    x.popleft()
                x.extend(z)
            print(1)
            line1.set_ydata(y)
            line2.set_ydata(x)
            print(3)
            fig.canvas.draw()
            fig.canvas.flush_events()
            print(2)
            file.write(' '.join(map(str, v)))
            file.write('\n')
            #plt.pause(0.1)
except KeyboardInterrupt:
    plt.close()
    file.close()
    my_serial.close()
    print('Bye')