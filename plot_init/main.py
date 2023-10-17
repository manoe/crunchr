#!/bin/python3

import yaml
import argparse
import matplotlib.pyplot as plt
import sys
import numpy as np


def check_status(stats, node, percent, count):
    decision = {}
    for i in stats:
        if stats[i] >= count:
            decision[i] = True
    if len(decision)/node >= percent:
        return True
    return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_init', description='Plot protocol init time', epilog=':-(')
    parser.add_argument('-i', '--image',
                        action='store_true', dest='image')
    parser.add_argument('-n', '--node', action='store', dest='node', default=63, type=int)
    parser.add_argument('-p', '--percent', action='store', dest='percent', default='0.9')
    parser.add_argument('-c', '--count', action='store', dest='count', default=10, type=int)
    parser.add_argument('-d', '--data', action='store_true', dest='data')
    parser.add_argument('filename', help='use ``-\'\' for stdin')

    args = parser.parse_args()

    args.percent = [float(x) for x in args.percent.split()]
    args.percent.sort()

    stream = sys.stdin
    if args.filename != '-':
        stream = open(args.filename, 'r')

    loader = yaml.safe_load(stream)

    pkt_list = {}
    fail = 0

    data = []

    for k in args.percent:
        for j in loader['runs']:
            pkt_list = {}
            for i in j['pkt_list']:
                if i['source'] in pkt_list:
                    pkt_list[i['source']] += 1
                else:
                    pkt_list[i['source']] = 1
                if check_status(pkt_list, args.node, k, args.count):
                    data.append({'timestamp': i['timestamp'],
                                 'energy':    i['energy'],
                                 'percent':  k})
                    if args.data:
                        print(str(i['timestamp']) + '#' + str(l) + '#' + str(i['energy']))
                    else:
                        print(str(k) + ' of active nodes reached at ' + str(i['timestamp'])+' with criteria of '
                              + str(args.count) + ' packets and ' + str(i['energy']) + ' J of energy')
                    fail -= 1
                    break
            fail += 1

    if fail > 0:
        print('Init criteria not met')

    y_nrg = [np.average([x['energy'] for x in data if x['percent'] == p]) for p in args.percent]
    y_time = [np.average([x['timestamp'] for x in data if x['percent'] == p]) for p in args.percent]

    plt.bar(args.percent, y_nrg)
    plt.show()
    print(y_nrg)
    print(y_time)