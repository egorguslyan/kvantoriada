import matplotlib.pyplot as plt
from collections import deque

file = open('dataCalmEKG4.txt')
plt.ion()
l = [128] * 512
y = deque(l)
size = 16
s = file.readline()
try:
    while s != '':
        s = s[:-1]
        l = s.split()
        data = list(map(int, l))
        for i in range(0, len(data), size):
            for j in range(size):
                y.popleft()
            y.extend(data[i : i + size])
            #plt.ylim(0, 256)
            plt.clf()
            plt.axes([0, 0, 512, 512])
            #plt.subplot(2, 1, 1)
            plt.plot(y)
            plt.draw()
            plt.gcf().canvas.flush_events()
        s = file.readline()
except KeyboardInterrupt:
    plt.close()
    file.close()
    print('Bye')
finally:
    file.close()
    plt.close()