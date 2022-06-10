import serial
import serial.tools.list_ports
import pandas as pd


def read(com, file_path, time=15, size=32):
    size_package = 200 * time

    available_ports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
    if com not in available_ports:
        return False

    with serial.Serial(com, 38400, timeout=0.1) as my_serial:
        a = int.from_bytes(my_serial.read(), 'little')
        while a != 255:
            if my_serial.in_waiting > 0:
                a = int.from_bytes(my_serial.read(), 'little')

        ecg = []
        for _ in range(size_package // size):
            v = [0] * size
            i = 0
            while i < size:
                if my_serial.in_waiting > 0:
                    v[i] = int.from_bytes(my_serial.read(), 'little')
                    i += 1

            ecg.extend(v)

        while a != 254:
            if my_serial.in_waiting > 0:
                a = int.from_bytes(my_serial.read(), 'little')

        eeg = []
        for _ in range(size_package // size):
            v = [0] * size
            i = 0
            while i < size:
                if my_serial.in_waiting > 0:
                    v[i] = int.from_bytes(my_serial.read(), 'little')
                    i += 1

            eeg.extend(v)

        data = pd.DataFrame([ecg, eeg, None], columns=['ecg', 'eeg', 'gsr'])
        data.to_csv(file_path, index=False)

    return True
