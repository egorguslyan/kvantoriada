import serial


def read(com, file_path, time=15, size=32):
    size_package = 200 * time
    my_serial = serial.Serial(com, 38400, timeout=0.1)
    file = open(file_path, 'w')
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

        #yield v
