#!/bin/python3
import argparse
import errno

import yaml
import matplotlib.pyplot as plt
import numpy as np
import sys
import networkx
# import scipy as sp


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog= 'pdr_hop_stat', description='Parse protocol logs and calculate pdr', epilog=':-(')
    parser.add_argument('-i', '--image',
                        action='store_true', dest='image')
    parser.add_argument('filename')

    args = parser.parse_args()

    stream = open(args.filename, 'r')

    loader = yaml.safe_load(stream)

    runs = loader['runs']
    loc_pdr_hist = []
    loc_pdr_per_hop_hist = {}

    for run in runs:
        # print(run['seed'])
        pdr_arr = list(run['pdr'].values())[1:]
        run['avg_pdr'] = np.average(pdr_arr)
        run['std_pdr'] = np.std(pdr_arr)
        run['disconn'] = pdr_arr.count(0)
        # print(run['std_pdr'])

        loc_pdr = []
        for i in run['loc_pdr']:
            if 'routing_table' in i:
                for j in i['routing_table']:
                    pdr = 0
                    for k in run['loc_pdr']:
                        if k['node'] == j['node'] and 'recv_table' in k:
                            for l in k['recv_table']:
                                if l['node'] == i['node']:
                                    pdr = l['pkt_count']/j['pkt_count']
                                    loc_pdr.append(pdr)
                                    if not j['hop'] in loc_pdr_per_hop_hist:
                                        loc_pdr_per_hop_hist.update({j['hop']: {'pdr': [], 'meas_pdr': []}})
                                    loc_pdr_per_hop_hist[j['hop']]['pdr'].append(pdr)
                                    meas=next((item for item in i['rreq_table'] if item['node'] == j['node']), None)
                                    loc_pdr_per_hop_hist[j['hop']]['meas_pdr'].append(
                                        meas['ack_count'] / meas['pkt_count'])
        run['avg_loc_pdr'] = np.average(loc_pdr)
        loc_pdr_hist.extend(loc_pdr)

    avg_pdr = []
    std_pdr = []
    disconn = []
    avg_loc_pdr = []

    for run in runs:
        avg_pdr.append(run['avg_pdr'])
        std_pdr.append(run['std_pdr'])
        disconn.append(run['disconn'])
        avg_loc_pdr.append(run['avg_loc_pdr'])
    print('Average pdr:     ' + str(np.average(avg_pdr)))
    print('Average std:     ' + str(np.average(std_pdr)))
    print('Average disconn: ' + str(np.average(disconn)))
    print('Average loc pdr: ' + str(np.average(avg_loc_pdr)))

    values = []
    bins = np.arange(-1.1, 1.1, 0.1)
    for i in loc_pdr_per_hop_hist:
        plt.subplot(2, int(np.ceil(len(loc_pdr_per_hop_hist.keys()) / 2)), i+1)
        plt.hist( [ p-mp for (p, mp) in zip(loc_pdr_per_hop_hist[i]['pdr'], loc_pdr_per_hop_hist[i]['meas_pdr'])], bins)
        # plt.hist(loc_pdr_per_hop_hist[i]['pdr'], bins)
        plt.title('Hop:'+str(i))
        print('Hop: '+str(i)+' PDR: '+str(np.average(loc_pdr_per_hop_hist[i]['pdr'])))

    plt.tight_layout()

    if args.image:
        plt.savefig(args.filename.replace('yaml', '_diff.png'), bbox_inches='tight')
    else:
        plt.show()

    bins = np.arange(0, 1.1, 0.1)
    for i in loc_pdr_per_hop_hist:
        plt.subplot(2, int(np.ceil(len(loc_pdr_per_hop_hist.keys()) / 2)), i+1)
        plt.hist(loc_pdr_per_hop_hist[i]['pdr'], bins)
        plt.title('Hop:'+str(i))
        print('Hop: '+str(i)+' PDR: '+str(np.average(loc_pdr_per_hop_hist[i]['pdr'])))
    plt.tight_layout()

    if args.image:
        plt.savefig(args.filename.replace('yaml', '_pdr.png'), bbox_inches='tight')
    else:
        plt.show()