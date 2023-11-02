#!/bin/python3

import yaml
import argparse
import matplotlib.pyplot as plt
import math
import numpy as np

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_depletion', description='Plot node depletion over time', epilog=':-(')
    parser.add_argument('filename', help='use ``-\'\' for stdin', nargs='+')

    args = parser.parse_args()

    files = args.filename

    arr = {}
    timestamp = {}
    for file in files:
        stream = open(file, 'r')
        loader = yaml.safe_load(stream)

        arr[file] = np.ndarray(shape=(len(loader['nrg_list']), len(loader['nrg_list'][0]['nodes'])))
        arr[file].fill(0.0)

        timestamp[file] = []
        idx = 0
        for i in loader['nrg_list']:
            timestamp[file].append(i['timestamp'])
            arr[file][idx][:] = [e['energy'] for e in i['nodes']]
            idx += 1

    rows = 2
    columns = math.ceil(len(files) / 2)
    idx = 0

    max_val = max([i.max() for i in arr.values()])

    print(max_val)

    for idx, file in enumerate(files):
        plt.subplot(rows, columns, idx + 1)
        plt.plot(timestamp[file], arr[file])
        plt.ylim(top=math.ceil(max_val))

        if args.event is not None:
            plt.axvline(x=args.event, color='r')
        plt.grid(True)
        plt.title(file)

    plt.show()

