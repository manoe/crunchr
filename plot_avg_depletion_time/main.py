#!/bin/python3

import math
import yaml
import argparse
import statistics
import matplotlib.pyplot as plt
import numpy as np


def calc_data_whatever(actual, prev):
    sum_sent_pkt = 0
    sum_recv_pkt = 0
    for idx, i in enumerate(actual['nodes']):
        sum_sent_pkt += i['report_sent'] - prev['nodes'][idx]['report_sent']
        sum_recv_pkt += i['report_recv'] - prev['nodes'][idx]['report_recv']
    return sum_sent_pkt, sum_recv_pkt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_avg_depletion_time',
                                     description='Plot average depletion time, if node is dead', epilog=':-(')
    parser.add_argument('-f', '--filename', help='filenames', nargs='+', required=True, dest='files')

    args = parser.parse_args()

    res = {}

    for file in args.files:
        stream = open(file, 'r')
        loader = yaml.safe_load(stream)
        dead_ts = []
        for i in loader['runs']:
            dead_node = []
            last_ts = i['nrg_list'][-1]['nodes']
            for j in last_ts:
                if j['energy'] == 0:
                    dead_node.append(j['node'])

            for j in i['nrg_list']:
                for k in j['nodes']:
                    if k['energy'] == 0 and k['node'] in dead_node:
                        dead_ts.append(j['timestamp'])
                        dead_node.remove(k['node'])
        res[file.split('/')[-1]] = dead_ts

    x = list(res.keys())
    y = [np.average(i) for i in res.values()]
    e = [np.std(i) for i in res.values()]

    plt.errorbar(x, y, e, linestyle='None', marker='^')
    plt.xticks(rotation=45, ha='right')
    plt.show()
