import serial
import serial.tools.list_ports
import pandas as pd


def get_available_ports():
    return [tuple(p)[0] for p in list(serial.tools.list_ports.comports())]


def read(com, file_path, timeECG=15, timeEEG=15, timeGSR=5, enableECG=1, enableEEG=1, enableGSR=1):
    enable = enableGSR & 1
    enable += (enableECG & 1) << 1
    enable += (enableEEG & 1) << 2

    config = [timeECG, timeEEG, timeGSR, enable]
    str_cfg = 'e' + ','.join(map(str, config)) + ';'
    # print(str_cfg)

    available_ports = get_available_ports()
    if com not in available_ports:
        return False

    try:
        with serial.Serial(com, 38400, timeout=0.1) as my_serial, open('log.txt', 'w') as log:
            ecg, eeg, gsr = [128, 128], [128, 128], [128, 128]
            for i in range(3):
                my_serial.write('c'.encode('ascii'))

            while my_serial.in_waiting <= 0:
                pass
            a = chr(int.from_bytes(my_serial.read(), "little"))
            log.write(a)
            while a != 's':
                if my_serial.in_waiting > 0:
                    a = chr(int.from_bytes(my_serial.read(), "little"))
                    log.write(a)
            my_serial.write(str_cfg.encode('ascii'))
            while True:
                while my_serial.in_waiting <= 0:
                    pass
                a = chr(int.from_bytes(my_serial.read(), "little"))
                log.write(a)
                while a != 'G' and a != 'C' and a != 'E' and a != 'f':
                    if my_serial.in_waiting > 0:
                        a = chr(int.from_bytes(my_serial.read(), "little"))
                        log.write(a)

                if a == 'f':
                    log.write(a)
                    break

                v = ' '
                while v != ';':
                    i = 0
                    while my_serial.in_waiting <= 0:
                        pass
                    v = chr(int.from_bytes(my_serial.read(), "little"))
                    log.write(v)
                    while v != ',' and v != ';':
                        if my_serial.in_waiting > 0:
                            i *= 10
                            i += int(v)
                            v = chr(int.from_bytes(my_serial.read(), "little"))
                            log.write(v)
                    log.write('(' + str(i) + ')')
                    if a == 'G':
                        gsr.append(i // 4)
                    elif a == 'C':
                        ecg.append(i // 4)
                    elif a == 'E':
                        eeg.append(i // 4)

            ecg = ' '.join(map(str, ecg))
            eeg = ' '.join(map(str, eeg))
            gsr = ' '.join(map(str, gsr))
            data = pd.DataFrame([[ecg, eeg, gsr], [timeECG, timeEEG, timeGSR], [enableECG, enableEEG, enableGSR]],
                                columns=['ecg', 'eeg', 'gsr'])
            data.to_csv(file_path, index=False)

        return True
    except serial.serialutil.SerialException:
        return False


if __name__ == "__main__":
    print(read("COM4", "res.csv", 15))
