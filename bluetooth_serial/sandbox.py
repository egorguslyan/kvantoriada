import serial
import serial.tools.list_ports
import time
import pandas as pd


def read(com, file_path, timeECG=15, timeEEG=15, timeGSR=5, enableECG=1, enableEEG=1, enableGSR=1):

    timeE = max(timeECG, timeEEG)
    enable = enableGSR & 1;
    enable += (enableECG & 1) << 1;
    enable += (enableEEG & 1) << 2;
    config = [timeECG, timeEEG, timeGSR, enable]
    str_cfg = 'e' + ','.join(map(str, config)) + ';'

    available_ports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
    if com not in map(lambda x: x[0], available_ports):
        return False

    with serial.Serial(com, 38400, timeout=0.1) as my_serial:
        ecg = eeg = gsr = []
        while my_serial.in_waiting <= 0:
            time.sleep(1)
            my_serial.write(str_cfg.encode('ascii'))
        while(True):
            while my_serial.in_waiting <= 0:
                pass
            a = chr(int.from_bytes(my_serial.read(), "little"))
            while a != 'G' and a != 'C' and a != 'E' and a != 'f':
                if my_serial.in_waiting > 0:
                    a = chr(int.from_bytes(my_serial.read(), "little"))

            if(a == 'f'):
                break

            v = ' '
            while v != ';':
                i = 0
                while my_serial.in_waiting <= 0:
                    pass
                v = chr(int.from_bytes(my_serial.read(), "little"))
                while v != ',' and v != ';':
                    if my_serial.in_waiting > 0:
                        i *= 10
                        i += int(v)
                        v = chr(int.from_bytes(my_serial.read(), "little"))
                if(a == 'G'):
                    gsr.append(i)
                elif(a == 'C'):
                    ecg.append(i)
                elif(a == 'E'):
                    eeg.append(i)

        gsr = [0]
        ecg = ' '.join(map(str, ecg))
        eeg = ' '.join(map(str, eeg))
        gsr = ' '.join(map(str, gsr))
        data = pd.DataFrame([[ecg, eeg, gsr]], columns=['ecg', 'eeg', 'gsr'])
        data.to_csv(file_path, index=False)

    return True

print(read("COM4", "res.csv", 15))