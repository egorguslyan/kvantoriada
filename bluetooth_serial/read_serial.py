import serial
import serial.tools.list_ports


def read(com, file_path, time=15, size=32):
    size_package = 200 * time

    myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
    if com not in myports:
        return False

    with open(file_path, 'w') as file, serial.Serial(com, 38400, timeout=0.1) as my_serial:
        a = int.from_bytes(my_serial.read(), 'little')
        while a != 255:
            if my_serial.in_waiting > 0:
                a = int.from_bytes(my_serial.read(), 'little')

        for _ in range(size_package // size):
            v = [0] * size
            i = 0
            while i < size:
                if my_serial.in_waiting > 0:
                    v[i] = int.from_bytes(my_serial.read(), 'little')
                    i += 1

            file.write(' '.join(map(str, v)))
            file.write(' ')

    return True
