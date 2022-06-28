import serial
import serial.tools.list_ports
import pandas as pd


def read(com, file_path, time=15):

    available_ports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
    if com not in available_ports:
        return False

    with serial.Serial(com, 38400, timeout=0.1) as my_serial:
        for(i in range(time)):
            a = my_serial.read()
            while a != 'G' and a != 'C' and a != 'E':
                if my_serial.in_waiting > 0:
                    a = my_serial.read()

            ecg = eeg = gsr = []
            v = ','
            while v != ';':
                i = 0
                while v != ',' and v != ';':
                    if my_serial.in_waiting > 0:
                        v = my_serial.read()
                        i *= 10
                        i += int(v)
                if(a == 'G')
                    gsr.append(i)
                if(a == 'C')
                    ecg.append(i)
                if(a == 'E')
                    eeg.append(i)

            data = pd.DataFrame([ecg, eeg, gsr], columns=['ecg', 'eeg', 'gsr'])
            data.to_csv(file_path, index=False)

    return True