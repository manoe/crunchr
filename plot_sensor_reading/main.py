#!/bin/env python3

import argparse
import yaml
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_sensor_reading', description='Plot sensor reading', epilog=':-(')
    parser.add_argument('-f', '--file', dest='filename', help='Filename, $1 for variable, $2 for seed')
    args = parser.parse_args()

    for f in args.filename:
        loader = yaml.safe_load(open(f, 'r'))

        arr = []

        for i in loader:
            if i['sensor_value'] != 0:
                arr.append(i['sensor_value'])

        bins = np.arange(0,8.1,0.5)

        counts, bins = np.histogram(arr, bins)
        plt.stairs(counts, bins)
    plt.show()