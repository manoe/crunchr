#!/bin/env python3

import yaml
import pandas as pd
import numpy as np
import argparse
import logging
import itertools as it
logger = logging.getLogger(__name__)
import sys


def gen_diff(table):
    res = pd.DataFrame(index=table.index, columns=table.columns[1:])

    for i in table.index:
        row = list(table.loc[i])
        res.loc[i] = [b-a for a,b in zip(row[:-1], row[1:])]
    return res


def get_attribute_list(pkt_list, attribute):
    res = pd.Series()
    for i in pkt_list:
        if i['role'] != 'central':
            res.at[i['node']] = i[attribute]
    return res


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='meas_4_proc_ff', description='Process ff related data ', epilog=':-(')
    parser.add_argument('-f', '--file', dest='filename', help='Filename, use $1 for frame counter')
    parser.add_argument('-l', '--log-level', dest='log_level', choices=['debug','info','none'], default='none', help='Log level')
    parser.add_argument('-c', '--count', dest='count', type=int, help='Count of frames')
    parser.add_argument('-o', '--out', dest='out_file', type=str, help='Count of frames', default='out')
    args = parser.parse_args()

    match args.log_level:
        case 'debug':
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        case 'info':
            logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    filename = args.filename.replace('$1', str(0))
    logger.info('Init filename: ' + str(filename))
    stream = open(filename, 'r')
    loader = yaml.safe_load(stream)
    pkts = pd.DataFrame(index=[i['node'] for i in loader['nodes'] if i['role'] != 'central'],
                             columns=[i for i in np.arange(-1, args.count)], data=0)

    living = pd.DataFrame(index=[i['node'] for i in loader['nodes'] if i['role'] != 'central'],
                             columns=[i for i in np.arange(0, args.count)], dtype=bool, data=False)

    mobility = pd.DataFrame(index=[i['node'] for i in loader['nodes']],
                                  columns=[i for i in np.arange(0, args.count)], data=False)

    timestamps = []
    for i in range(args.count):
        filename = args.filename.replace('$1', str(i))
        logger.info('Actual filename: ' + str(filename))

        stream = open(filename, 'r')
        loader = yaml.safe_load(stream)
        timestamp = loader['timestamp']
        timestamps.append(timestamp)

        pkts[i] = get_attribute_list(loader['nodes'], 'report_recv')
        living[i] = get_attribute_list(loader['nodes'], 'state').map(lambda x: True if x == 'live' else False)
        mobility[i] = get_attribute_list(loader['nodes'], 'mobility')
    reachable = gen_diff(pkts).map(lambda x: True if x > 0 else False)

    reachable_count = [reachable[i].value_counts()[True]  for i in reachable]
    living_count = [living[i].value_counts()[True] if True in living[i].value_counts() else 0 for i in living]
    dead_count = [living[i].value_counts()[False] if False in living[i].value_counts() else 0 for i in living]
    mobility_count  = [mobility[i].value_counts()[True] if True in mobility[i].value_counts() else 0 for i in mobility]


    out=pd.DataFrame(index=timestamps)
    out['r']=reachable_count
    out['l']=living_count
    out['d']=dead_count
    out['m']=list(it.accumulate(mobility_count))
    out.to_pickle(args.out_file+'.pickle')