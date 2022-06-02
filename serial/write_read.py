import serial
import matplotlib.pyplot as plt

my_serial = serial.Serial('COM6', 38400, timeout=0.1)
file = open('dataCalmGSR2.txt', 'a')
try:
    while True:
        a = int.from_bytes(my_serial.read(), 'little')
        if a == 255:
            v = [0] * 512
            i = 0
            while i < 512:
                if my_serial.in_waiting > 0:
                    v[i] = int.from_bytes(my_serial.read(), 'little')
                    i += 1
            z = [0] * 512
            i = 0
            while i < 512:
                if my_serial.in_waiting > 0:
                    z[i] = int.from_bytes(my_serial.read(), 'little')
                    i += 1
            plt.close()
            plt.plot(v, 'b')
            plt.plot(z, 'r')
            plt.show(block=False)
            file.write(' '.join(map(str, v)))
            file.write(',')
            file.write(' '.join(map(str, z)))
            file.write('\n')
            plt.pause(0.1)
except KeyboardInterrupt:
    plt.close()
    file.close()
    my_serial.close()
    print('Bye')