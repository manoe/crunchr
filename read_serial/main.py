#!/bin/env python3

import serial
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='read_serial', description='Read stuff from serial port', epilog=':-(')
    parser.add_argument('-b', '--baud', dest='baud', type=int, help='Baud rate', default=921600)
    parser.add_argument('-d', '--device', dest='device', type=str, help='Serial device', default='/dev/ttyUSB0')
    args = parser.parse_args()

    ser = serial.Serial(args.device, args.baud, timeout=1)
    print(ser.portstr)

    line = ser.readline()

    print(line)

    ser.close()
