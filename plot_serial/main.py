#!/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import argparse
from scipy.ndimage import uniform_filter1d

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='read_serial', description='Read stuff from serial port', epilog=':-(')
    parser.add_argument('-f', '--file', dest='file', type=str, help='File to be read', default='output.pickle')
    parser.add_argument('-a', '--average', dest='average', type=int, help='Apply moving average')
    parser.add_argument('-s', '--skip', dest='skip', type=int, help='Skip samples', default=0)
    args = parser.parse_args()

    arr = pd.read_pickle(args.file)
    if args.average:
        plt.plot(arr['t'][args.skip:], uniform_filter1d(arr['s'][args.skip:], size=args.average), label='Short term')
        plt.plot(arr['t'][args.skip:], uniform_filter1d(arr['l'][args.skip:], size=args.average), label='Long term')

    else:

        plt.plot(arr['t'][args.skip:], arr['s'][args.skip:], label='Short term')
        plt.plot(arr['t'][args.skip:], arr['l'][args.skip:], label='Long term')
    plt.grid(True)
    plt.xlim([arr['t'].iloc[args.skip], arr['t'].iloc[-1]])
    a = plt.xticks()
    plt.legend()

    plt.tight_layout()
    plt.show()