import matplotlib.pyplot as plt
import time
from collections import deque

file = open('dataCalm2.txt')
s = file.readline()

plt.ion()

s = s[:-1]
l = s.split()
y = deque(map(int, l))

plt.clf()

plt.subplot(2, 1, 1)
plt.plot(y)
plt.draw()
#plt.gcf().canvas.flush_events()
#time.sleep(0.001)
plt.subplot(2, 1, 2)
plt.plot(y)
plt.draw()
plt.gcf().canvas.flush_events()
#time.sleep(0.001)


size = 16

s = file.readline()
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

        plt.subplot(2, 1, 1)
        plt.plot(y)
        plt.draw()
        #plt.gcf().canvas.flush_events()
        #time.sleep(0.001)
        plt.subplot(2, 1, 2)
        plt.plot(y)
        plt.draw()
        plt.gcf().canvas.flush_events()

    s = file.readline()
file.close()