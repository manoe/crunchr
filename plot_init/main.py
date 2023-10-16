#!/bin/python3

import yaml
import argparse
import matplotlib.pyplot as plt
import sys


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
    parser.add_argument('-p', '--percent', action='store', dest='percent', default=0.9, type=float)
    parser.add_argument('-c', '--count', action='store', dest='count', default=10, type=int)
    parser.add_argument('-d', '--data', action='store_true', dest='data')
    parser.add_argument('filename', help='use ``-\'\' for stdin')

    args = parser.parse_args()

    stream = sys.stdin
    if args.filename != '-':
        stream = open(args.filename, 'r')

    loader = yaml.safe_load(stream)

    pkt_list = {}
    fail = True

    for j in loader['runs']:
        fail = True
        pkt_list = {}
        for i in j['pkt_list']:
            if i['source'] in pkt_list:
                pkt_list[i['source']] += 1
            else:
                pkt_list[i['source']] = 1
            if check_status(pkt_list, args.node, args.percent, args.count):
                fail = False
                if args.data:
                    print(str(i['timestamp']) + '#' + str(args.percent) + '#' + str(i['energy']))
                else:
                    print(str(args.percent) + ' of active nodes reached at ' + str(i['timestamp'])+' with criteria of '
                          + str(args.count) + ' packets and ' + str(i['energy']) + ' J of energy')
                break

    if fail:
        print('Init criteria not met')
