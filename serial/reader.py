import matplotlib.pyplot as plt

file = open('dataCalm2.txt')
s = file.readline()
while s != '':
    s = s[:-1]
    l = s.split()
    data = list(map(int, l))
    s = file.readline()
    plt.plot(data)
    plt.show(block=False)
    plt.pause(0.5)
    plt.clf()
file.close()
