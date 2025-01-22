#!/bin/env python3

import argparse
import logging
import pandas as pd

logger = logging.getLogger(__name__)
import sys
import numpy as np
import yaml

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='proc_depletion_data', description='Process BLT and LT data', epilog=':-(')
    parser.add_argument('-e', '--energy', dest='nrg_file', action='store', help='The energy file', required=True)
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    parser.add_argument('-o', '--output', dest='output', action='store', help='Output file', default='data')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    lt = {i : [] for i in ['lt', 'blt']}

    stream = open(args.nrg_file, 'r')
    nrg_yml = yaml.safe_load(stream)
    logger.debug('filename: '+str(args.nrg_file))
    for i in nrg_yml['nrg_list']:
        b_nrg_arr = [ n['energy'] for n in i['nodes'] if n['role'] == 'border']
        nrg_arr = [ n['energy'] for n in i['nodes']]

        if min(b_nrg_arr) == 0:
            lt['blt'].append(i['timestamp'])
        if min(nrg_arr) == 0:
            lt['lt'].append(i['timestamp'])

    res = pd.DataFrame(columns=['lt', 'blt'])
    res_data = []
    for i in ['lt', 'blt']:
        if len(lt[i]) > 0:
            res_data.append(min(lt[i]))
        else:
            res_data.append(np.nan)

    res.loc[0]=res_data
    logger.debug('result: '+str(res))
    pd.to_pickle(res, args.output+'.pickle')