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
    parser = argparse.ArgumentParser(prog='plot_pkt_vs_node_loss',
                                     description='Plot received packets vs node loss over time', epilog=':-(')
    parser.add_argument('-n', '--frame_num', action='store', dest='frame_num', default=10, type=int,
                        help='Calculate with every nth frame')
    parser.add_argument('-H', '--hop', action='store', dest='hop', default=3, type=int,
                        help='Count nodes with hop')
    parser.add_argument('-f', '--filename', help='filenames', nargs='+', required=True, dest='files')

    args = parser.parse_args()
    res = {}

    for file in args.files:
        stream = open(file, 'r')
        loader = yaml.safe_load(stream)
        runs = []
        for i in loader['runs']:
            pkt_run = {}
            for idx, j in enumerate(i['nrg_list']):
                if idx % args.frame_num == 0:
                    pkt_run[j['timestamp']] = sum([i['report_recv'] for i in j['nodes']])

            runs.append(dict(zip(list(pkt_run.keys())[1:], list(np.subtract(list(pkt_run.values())[1:], list(pkt_run.values())[:-1])))))
        x = list(runs[0].keys())
        res[file] = np.average([list(run.values()) for run in runs], axis=0)
    print([res[file] for file in res.keys()])
    plt.plot(x, np.array([res[file] for file in res.keys()]).transpose())
    plt.legend(res.keys())
    plt.show()
