#!/bin/env python3

import yaml
import argparse
import numpy as np
import pandas as pd

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='calc_pdr.py', description='Calculate PDR', epilog=':-(')
    parser.add_argument('-e', '--event', dest='event', action='store_true')
    parser.add_argument('-n', '--node', dest='node', type=float)
    parser.add_argument('-f', '--file', dest='file', required=True)
    parser.add_argument('-p', '--pandas', dest='pandas', action='store_true')
    parser.add_argument('-o', '--out', dest='out', default='out.pickle')
    parser.add_argument('-m', '--minimal', dest='minimal', action='store_true')

    args = parser.parse_args()

    loader = yaml.safe_load(open(args.file, 'r'))

    if 'runs' in loader:
        data_source = loader['runs'][0]
    else:
        data_source = loader

    pkt_cat = 'report_pdr_new'
    if args.event:
        pkt_cat = 'event_pdr_new'

    if args.node:
        pdr_arr = [i[pkt_cat] for i in data_source['pdr'] if pkt_cat in i and i['node'] == args.node]
    else:
        pdr_arr = [i[pkt_cat] for i in data_source['pdr'] if pkt_cat in i]

    pdr = np.average(pdr_arr)
    if args.pandas:
        pd.Series(pdr).to_pickle(args.out)
    else:
        if args.minimal:
            print(pdr)
        else:
            print('Average PDR: '+str(pdr))
