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
    parser.add_argument('-n', '--node', action='store', dest='node', default=63)
    parser.add_argument('-p', '--percent', action='store', dest='percent', default=0.9)
    parser.add_argument('-c', '--count', action='store', dest='count', default=10)
    parser.add_argument('filename', help='use ``-\'\' for stdin')

    args = parser.parse_args()

    stream = sys.stdin
    if args.filename != '-':
        stream = open(args.filename, 'r')

    loader = yaml.safe_load(stream)

    pkt_list = {}

    for i in loader:
        if i['source'] in pkt_list:
            pkt_list[i['source']] += 1
        else:
            pkt_list[i['source']] = 1
        if check_status(pkt_list, args.node, args.percent, args.count):
            print(i['timestamp'])

    print('Init criteria not met')
