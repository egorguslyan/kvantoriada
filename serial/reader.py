import matplotlib.pyplot as plt
import time

def f(o):
    o = int(o)
    if o > 255:
        return 128
    else:
        return o


file = open('data1.txt')
s = file.readline()
d = list(map(f, s.split()))
print(len(d))
for i in range(56):
    e = d[i*512:(i+1)*512-1]
    e.append(128)
    #print(e)
    plt.plot(e)
    plt.show(block=False)
    plt.pause(0.5)
    plt.close()
file.close()
