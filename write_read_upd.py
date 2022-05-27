import serial
import matplotlib.pyplot as plt
from collections import deque

size = 16
plt.ion()

my_serial = serial.Serial('COM6', 38400, timeout=0.1)
file = open('dataCalmTestGsr.txt', 'a')

y = deque()
x = deque()

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
            plt.clf()
            print(2)
            plt.subplot(2, 1, 1)
            plt.plot(y)
            plt.draw()
            plt.subplot(2, 1, 2)
            plt.plot(x)
            plt.draw()
            print(8)
            plt.gcf().canvas.flush_events()
            print(9)
            file.write(' '.join(map(str, v)))
            file.write('\n')
            #plt.pause(0.1)
except KeyboardInterrupt:
    plt.close()
    file.close()
    my_serial.close()
    print('Bye')