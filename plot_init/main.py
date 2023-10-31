#!/bin/python3

import yaml
import argparse
import matplotlib.pyplot as plt
import sys
import numpy as np
from matplotlib.ticker import FormatStrFormatter

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
    parser.add_argument('-p', '--percent', action='store', dest='percent', default='0.9',
                        help='list of percents, e.g. \'0.1 0.2\'')
    parser.add_argument('-c', '--count', action='store', dest='count', default=10, type=int)
    parser.add_argument('-d', '--data', action='store_true', dest='data')
    parser.add_argument('filename', help='use ``-\'\' for stdin')

    args = parser.parse_args()

    args.percent = [float(x) for x in args.percent.split()]
    args.percent.sort()

    files = args.filename.split()

    y_nrg = {}
    y_time = {}

    for filename in files:
        if filename == '-':
            stream = sys.stdin
        else:
            stream = open(filename, 'r')

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
            print('Init criteria not met x'+str(fail)+' times')

        y_nrg[filename] = [np.average([x['energy'] for x in data if x['percent'] == p]) for p in args.percent]
        y_time[filename] = [np.average([x['timestamp'] for x in data if x['percent'] == p]) for p in args.percent]

    plt.subplot(2,1,1)

    bc = plt.bar([ x - 0.2 for x in range(len(args.percent))], list(y_nrg.values())[0], 0.4, label=list(y_nrg.keys())[0])
    plt.bar_label(bc,label=args.percent)
    bc = plt.bar([ x + 0.2 for x in range(len(args.percent))], list(y_nrg.values())[1], 0.4, label=list(y_nrg.keys())[1])
    plt.bar_label(bc, label=args.percent)
    plt.title('Consumed energy vs. initialization percentage')
    plt.xticks(range(len(args.percent)), labels=args.percent)

    plt.subplot(2,1,2)
    bc = plt.bar([ x - 0.2 for x in range(len(args.percent))], list(y_time.values())[0], 0.4, label=list(y_time.keys())[0])
    plt.bar_label(bc,label=args.percent)
    bc = plt.bar([ x + 0.2 for x in range(len(args.percent))], list(y_time.values())[1], 0.4, label=list(y_time.keys())[1])
    plt.bar_label(bc, label=args.percent)
    plt.title('Elapesed time vs. initialization percentage')
    plt.xticks(range(len(args.percent)), labels=args.percent)

    plt.legend()
    plt.show()
