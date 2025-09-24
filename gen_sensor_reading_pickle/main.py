#!/bin/env python3

import pandas as pd
import yaml
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='gen_sensor_reading_pickle', description='Gen pickles, yeah', epilog=':-(')
    parser.add_argument('-f', '--filename', dest='filename')
    parser.add_argument('-o', '--out', dest='out')
    
    args = parser.parse_args()

    loader = yaml.safe_load(open(args.filename, 'r'))

    arr = {'timestamp': [], 'node': [], 'sensor_value': []}
    for i in loader:
        arr['timestamp'].append(i['timestamp'])
        arr['node'].append(i['node'])
        arr['sensor_value'].append(i['sensor_value'])


    pd.DataFrame(arr).to_pickle(args.out+'.pickle')