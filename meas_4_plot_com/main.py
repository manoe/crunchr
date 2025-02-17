#!/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import yaml
import sys
import argparse
import logging
import pandas as pd
logger = logging.getLogger(__name__)
from matplotlib import rcParams
rcParams['font.family'] = ['serif']
rcParams['font.serif'] = ['Times New Roman']


def get_attribute_list(pkt_list, attribute):
    res = pd.DataFrame()
    for i in pkt_list['nrg_list']:
        for j in i['nodes']:
            if j['role'] != 'central':
                res.at[j['node'],i['timestamp']] = j[attribute]
    return res


def get_recv_pkt_list(pkt_list):
    return get_attribute_list(pkt_list, 'report_recv')


def get_state_list(pkt_list):
    return get_attribute_list(pkt_list, 'state')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='meas_4_plot_com', description='Plot protocol ', epilog=':-(')
    parser.add_argument('-f','--file', dest='filename', help='Filename')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    parser.add_argument('-i', '--info', dest='info', choices=['report_pdr', 'event_pdr'], default='report_pdr', help='What info to use')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    logger.debug('Base filename: ' + str(args.filename))

    stream = open(args.filename, 'r')
    loader = yaml.safe_load(stream)

    recv_pkt_list = get_recv_pkt_list(loader)



#    fig, axs = plt.subplots(nrows=len(args.proto2), ncols=1, layout='compressed', figsize=(4, 12))

