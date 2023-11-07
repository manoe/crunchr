#!/bin/python3

import math
import yaml
import argparse
import matplotlib.pyplot as plt
import sys
import numpy as np


def sum_list_prop(list_prop):
    return [sum([x[list_prop] for x in i['nodes']]) for i in loader['nrg_list']]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_pdr_nrg', description='Plot network pdr and energy over time', epilog=':-(')
    parser.add_argument('filename', help='use ``-\'\' for stdin', nargs='+')
    parser.add_argument('-e', '--event', dest='event', type=int)

    args = parser.parse_args()

    files = args.filename

    sent_report_pkt = {}
    recv_report_pkt = {}
    timestamp = {}

    for file in files:
        stream = open(file, 'r')

        loader = yaml.safe_load(stream)

        sum_sent_report = sum_list_prop('report_sent')
        sum_recv_report = sum_list_prop('report_recv')

        sent_report_pkt[file] = np.subtract(sum_sent_report[1:], sum_sent_report[:-1])
        recv_report_pkt[file] = np.subtract(sum_recv_report[1:], sum_recv_report[:-1])

        timestamp[file] = [round(i['timestamp'], 0) for i in loader['nrg_list']][:-1]

    rows = 2 if len(files) > 1 else 1
    columns = math.ceil(len(files)/2)

    max_val = max([i.max() for i in sent_report_pkt.values()])
    min_val = min([i.min() for i in recv_report_pkt.values()])

    for idx, file in enumerate(files):
        plt.subplot(rows, columns, idx+1)
        plt.plot(timestamp[file], np.transpose(np.array([sent_report_pkt[file], recv_report_pkt[file]])))
        plt.ylim(top=math.ceil(max_val/10.0)*10.0, bottom=math.floor(min_val))
        if args.event is not None:
            plt.axvline(x=args.event, color='r')
        plt.grid(True)
        plt.title(file.split('/')[-1])
    plt.legend(['Sent report pkt', 'Received report pkt'])

    plt.show()

