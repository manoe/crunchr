#!/bin/env python3
import argparse
import errno

import yaml
import numpy as np
import sys



if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='calc_radio', description='Parse protocol logs and calculate pdr', epilog=':-(')
    parser.add_argument('filename')

    args = parser.parse_args()
    stream = open(args.filename, 'r')

    loader = yaml.safe_load(stream)

    runs = loader['runs']

    radio = []

    for run in runs:
        for i in run['loc_pdr']:
            if 'radio' in i:
                radio.append(i['radio'])

    for i in list(radio[0].keys()):
        print(str("avg.")+str(i)+str(": ")+str( np.average([j[i] for j in radio  ])))
        print(str("std.")+str(i)+str(": ")+str( np.std([j[i] for j in radio  ])))


