#!/bin/python3
import argparse
import errno

import yaml
import matplotlib.pyplot as plt
import numpy as np
import sys
import networkx
# import scipy as sp


def reject_outliers(data, m=2):
    return data[abs(data - np.mean(data)) < m * np.std(data)]

def calc_rx_stat(radio_stat):
    rx_stat = {}
    rx_stat['rx_ok'] = radio_stat['RX_ok_no_interf']+radio_stat['RX_ok_interf']
    rx_stat['rx_fail'] = radio_stat['RX_fail_no_interf']+radio_stat['RX_fail_interf']+radio_stat['RX_fail_below_sensitivity']+radio_stat['RX_fail_not_rx_state']
    rx_stat['rx_interf'] = radio_stat['RX_fail_interf']+radio_stat['RX_ok_interf']
    rx_stat['rx_fail_interf'] = radio_stat['RX_fail_interf']
    return rx_stat

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='path_stat', description='Parse protocol logs and calculate path stuff', epilog=':-(')
    parser.add_argument('-i', '--image',
                        action='store_true', dest='image')
    parser.add_argument('-d', '--data',
                        action='store_true', dest='data')
    parser.add_argument('-n', '--no-header',
                        action='store_true', dest='no_header')
    parser.add_argument('-g', '--gap', dest='gap')
    parser.add_argument('-s', '--sheet',
                        action='store_true', dest='sheet')
    parser.add_argument('-r', '--remove-outlier',
                        action='store_true', dest='remove_outlier')

    parser.add_argument('filename')

    args = parser.parse_args()
    stream = open(args.filename, 'r')

    loader = yaml.safe_load(stream)

    runs = loader['runs']

    path_arr = []

    path_per_hop = {}

    for run in runs:
        for i in run['loc_pdr']:
            if i['state'] != 'INIT' and 'hop' in i and i['role'] == 'external':
                path_arr.append(len(i['routing_table']))
                if i['hop'] not in path_per_hop:
                    path_per_hop[i['hop']] = []
                path_per_hop[i['hop']].append(len(i['routing_table']))

    print('Average path/node: '+str(np.average(path_arr)))

    if args.image:
        bins = np.arange(0, np.max(path_arr), 1)
        j = 1
        for i in path_per_hop:
            plt.subplot(int(np.ceil(len(path_per_hop)/2)), 2, j)
            plt.hist(path_per_hop[i], bins)
            j = j+1
            plt.title('Hop:' + str(i))

#        plt.hist(path_arr, bins)
        plt.tight_layout()
        plt.show()

#                if i['hop'] not in pdr_per_hop_hist:
#                    pdr_per_hop_hist[i['hop']] = [run['pdr'][i['node']]]
#                    if 'routing_table' in i: # dunno if this really works
#                        path_per_hop_hist[i['hop']] = [len(i['routing_table'])]
#                    else:
#                        print('No routing table present: ' + str(i['node']))
#                else:
#                    pdr_per_hop_hist[i['hop']].append(run['pdr'][i['node']])
#                    if 'routing_table' in i:
#                        path_per_hop_hist[i['hop']].append(len(i['routing_table']))
#                    else:
#                        print('No routing table present: ' +str(i['node']))
#                radio_stat[-1]['pdr'] = run['pdr'][i['node']]
#
#            if 'routing_table' in i:
#                if i['role'] == 'external':
#                    paths.append(len(i['routing_table']))
#                for j in i['routing_table']:
#                    pdr = 0
#                    for k in run['loc_pdr']:
#                        if k['node'] == j['node'] and 'recv_table' in k:
#                            for l in k['recv_table']:
#                                if l['node'] == i['node']:
#                                    pdr = l['pkt_count']/j['pkt_count']
#                                    loc_pdr.append(pdr)
#                                    if not j['hop'] in loc_pdr_per_hop_hist:
#                                        loc_pdr_per_hop_hist.update({j['hop']: {'pdr': [], 'meas_pdr': []}})
#                                    loc_pdr_per_hop_hist[j['hop']]['pdr'].append(pdr)
##                                    meas=next((item for item in i['rreq_table'] if item['node'] == j['node']), None)
##                                    loc_pdr_per_hop_hist[j['hop']]['meas_pdr'].append(
##                                        meas['ack_count'] / meas['pkt_count'])
#        run['avg_loc_pdr'] = np.average(loc_pdr)
#        loc_pdr_hist.extend(loc_pdr)
#
#    avg_pdr = []
#    std_pdr = []
#    disconn = []
#    avg_loc_pdr = []
#
#    for i in radio_stat:
#        i['rx_stat'] = calc_rx_stat(i['radio'])
#
##    radio_stat.sort(key=lambda x: x['rx_stat']['rx_ok']/(x['rx_stat']['rx_fail']+x['rx_stat']['rx_ok']))
#    radio_stat.sort(key=lambda x: x['rx_stat']['rx_ok'] / (x['rx_stat']['rx_fail'] + x['rx_stat']['rx_ok']))
#
#    rx_rate = []
#    hop_arr = []
#    for i in radio_stat:
#        rx_rate.append(i['rx_stat']['rx_ok']/(i['rx_stat']['rx_fail']+i['rx_stat']['rx_ok']))
#        hop_arr.append(i['hop'])
#
#
#
#
#    for run in runs:
#        avg_pdr.append(run['avg_pdr'])
#        std_pdr.append(run['std_pdr'])
#        disconn.append(run['disconn'])
#        avg_loc_pdr.append(run['avg_loc_pdr'])
#
#    header = 'file#'
#    data = str(args.filename)+'#'
#
#    if args.sheet:
#        header += 'avg.pdr#avg.std#avg.disconn#avg.loc.pdr#avg.path'
#        data += str(np.average(avg_pdr))+'#'+str(np.average(std_pdr))+'#'+str(np.average(disconn))+'#'+str(np.average(avg_loc_pdr))+'#'+str(np.average(paths))
#    #    exit(0)
#    else:
#        print('Average pdr:     ' + str(np.average(avg_pdr)))
#        print('Average std:     ' + str(np.average(std_pdr)))
#        print('Average disconn: ' + str(np.average(disconn)))
#        print('Average loc pdr: ' + str(np.average(avg_loc_pdr)))
#        print('Average paths:   ' + str(np.average(paths)))
#
#    values = []
#    bins = np.arange(-1.1, 1.1, 0.1)
#    loc_pdr_per_hop_hist = dict(sorted(loc_pdr_per_hop_hist.items()))
#
#    for i in loc_pdr_per_hop_hist:
##        plt.subplot(2, int(np.ceil(len(loc_pdr_per_hop_hist.keys()) / 2)), i+1)
##        plt.hist( [ p-mp for (p, mp) in zip(loc_pdr_per_hop_hist[i]['pdr'], loc_pdr_per_hop_hist[i]['meas_pdr'])], bins)
#     # plt.hist(loc_pdr_per_hop_hist[i]['pdr'], bins)
##        plt.title('Hop:'+str(i))
#        if args.sheet:
#            header += '#hop.'+str(i)+'.pdr'
#            data += '#' + str(np.average(loc_pdr_per_hop_hist[i]['pdr']))
#        else:
#            print('Hop: '+str(i)+' PDR: '+str(np.average(loc_pdr_per_hop_hist[i]['pdr'])))
#
#    if args.gap:
#        gap = int(args.gap) - len(loc_pdr_per_hop_hist)
#        for i in range(0,gap):
#            header += ' # '
#            data += ' # '
##    plt.tight_layout()
#    new_pdr_per_hop_hist = []
#
#
#    pdr_per_hop_hist = dict(sorted(pdr_per_hop_hist.items()))
#
#    for i in pdr_per_hop_hist:
#        arr = []
#        for j in pdr_per_hop_hist[i]:
#            arr.append(j['pkt_recv'] / j['pkt_sent'])
#        if args.sheet:
#            header += '#e2e.hop.'+str(i)+'.pdr'
#            data += '#' + str(np.average(arr))
#        else:
#            print('Hop '+str(i)+' e2e PDR: '+str(np.average(arr)))
#
#    if args.gap:
#        gap = int(args.gap) - len(pdr_per_hop_hist)
#        for i in range(0, gap):
#            header += ' # '
#            data += ' # '
#    path_per_hop_hist = dict(sorted(path_per_hop_hist.items()))
#
#    for i in path_per_hop_hist:
#        if args.sheet:
#            header += '#hop.'+str(i)+'.path'
#            data += '#' + str(np.average(path_per_hop_hist[i]))
#        else:
#            print('Hop '+str(i)+' avg.path: '+str(np.average(path_per_hop_hist[i])))
#
#    if not args.data:
#        if args.image:
#            plt.savefig(args.filename.replace('yaml', '_diff.png'), bbox_inches='tight')
#        else:
#            plt.show()
#        plt.close()
##    bins = np.arange(0, 1.1, 0.1)
##    for i in loc_pdr_per_hop_hist:
##        plt.subplot(2, int(np.ceil(len(loc_pdr_per_hop_hist.keys()) / 2)), i+1)
##        plt.hist(loc_pdr_per_hop_hist[i]['pdr'], bins)
##        plt.title('Hop:'+str(i))
##    plt.tight_layout()
#
#    if not args.data:
#        if args.image:
#            plt.savefig(args.filename.replace('yaml', '_pdr.png'), bbox_inches='tight')
# #       else:
##            plt.show()
#
##    plt.close()
##    if not args.data:
##        plt.plot(rx_rate)
##        plt.plot(hop_arr)
##        plt.show()
#
##    np_rx = np.array(rx_rate)
##    np_hop = np.array(hop_arr)
#
##    m = np.row_stack((np_rx, np_hop))
##    ret = np.corrcoef(m)
#
#    if args.sheet:
#        if not args.no_header:
#            print(header)
#        print(data)