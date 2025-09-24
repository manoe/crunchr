#!/bin/env python3

import serial
import argparse
import string
import signal
import sys
import datetime
import pandas as pd

def signal_handler(sig, frame):
    print(pd.DataFrame(arr))
    pd.DataFrame(arr).to_pickle(str(time_start).replace(' ','_')+'.pickle')
    sys.exit(0)

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='read_serial', description='Read stuff from serial port', epilog=':-(')
    parser.add_argument('-b', '--baud', dest='baud', type=int, help='Baud rate', default=921600)
    parser.add_argument('-d', '--device', dest='device', type=str, help='Serial device', default='/dev/ttyUSB0')
    parser.add_argument('-t', '--test', dest='test', action='store_true', help='Test mode', default=False)
    args = parser.parse_args()

    if args.test:
        line = b'0.790\t0.769\t0.914\r\n'
        print(line.decode('UTF-8'))
        print(line.decode('UTF-8').split())
        exit(0)

    arr = {'t': [], 's': [], 'm':[], 'l': []}
    time_start = datetime.datetime.now()
    ser = serial.Serial(args.device, args.baud, timeout=1)
    print(ser.portstr)


    signal.signal(signal.SIGINT, signal_handler)

    while True:
        line = ser.readline()
        try:
            line.decode('UTF-8')
        except UnicodeDecodeError:
            continue
        print(line.decode('UTF-8'))
        res = line.decode('UTF-8').split()

        if all( [ is_float(i) for i in res ] ):
            res = [ float(i) for i in res if i ]
            if(len(res) == 3):
                arr['t'].append(datetime.datetime.now())
                arr['s'].append(res[0])
                arr['m'].append(res[1])
                arr['l'].append(res[2])
                print(str(arr['t'][-1])+' '+str(res))
    
    ser.close()

