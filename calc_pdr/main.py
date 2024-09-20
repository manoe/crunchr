#!/bin/env python3

import yaml
import argparse
import numpy as np

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='calc_pdr.py', description='Calculate PDR', epilog=':-(')
    parser.add_argument('-e', '--event', dest='event', action='store_true')
    parser.add_argument('-n', '--node', dest='node', type=float)
    parser.add_argument('-f', '--file', dest='file')

    args = parser.parse_args()

    if args.file is None:
        print('File missing')
        exit(0)

    loader = yaml.safe_load(open(args.file, 'r'))

    if 'runs' in loader:
        data_source = loader['runs'][0]
    else:
        data_source = loader

    pkt_cat = 'report_pdr'
    if args.event:
        pkt_cat = 'event_pdr'

    if args.node:
        pdr_arr = [i[pkt_cat] for i in data_source['pdr'] if pkt_cat in i and i['node'] == args.node]
    else:
        pdr_arr = [i[pkt_cat] for i in data_source['pdr'] if pkt_cat in i]
    pdr = np.average(pdr_arr)
    print('Average PDR: '+str(pdr))
