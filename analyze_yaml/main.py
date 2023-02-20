#!/bin/python3
import argparse
import errno

import yaml
import matplotlib.pyplot as plt
import numpy as np
import sys
import networkx
# import scipy as sp

def calc_rx_stat(radio_stat):
    rx_stat = {}
    rx_stat['rx_ok'] = radio_stat['RX_ok_no_interf']+radio_stat['RX_ok_interf']
    rx_stat['rx_fail'] = radio_stat['RX_fail_no_interf']+radio_stat['RX_fail_interf']+radio_stat['RX_fail_below_sensitivity']+radio_stat['RX_fail_not_rx_state']
    rx_stat['rx_interf'] = radio_stat['RX_fail_interf']+radio_stat['RX_ok_interf']
    rx_stat['rx_fail_interf'] = radio_stat['RX_fail_interf']
    return rx_stat

def configure_cmd_parser():
    parser = argparse.ArgumentParser(prog='analyze_yaml', description='Parse protocol stats and calculate metrics', epilog=':-(')
    parser.add_argument('-i', '--image',
                        action='store_true', dest='image')
    parser.add_argument('-d', '--data',
                        action='store_true', dest='data')
    parser.add_argument('-n', '--no-header',
                        action='store_true', dest='no_header')
    parser.add_argument('-g', '--gap', dest='gap')
    parser.add_argument('filename')
    return parser


def load_yaml(filename):
    stream = open(filename, 'r')
    return yaml.safe_load(stream)


def add_e2e_pdr_to_node(run, pdr_token):
    for i in run['pdr']:
        if pdr_token in i:
            for j in run['loc_pdr']:
                if j['node'] == i['node']:
                    j[pdr_token] = i[pdr_token]
    return run


def get_run_e2e_pdr(run, token):
    e2e_pdr = []
    for i in run['loc_pdr']:
        if token in i:
            e2e_pdr.append(i[token])
    return e2e_pdr


def get_run_e2e_pdr_per_hop(run, token):
    e2e_pdr_per_hop = {}
    for i in run['loc_pdr']:
        if token in i:
            if i['hop'] in e2e_pdr_per_hop:
                e2e_pdr_per_hop[i['hop']] += [i[token]]
            else:
                e2e_pdr_per_hop[i['hop']] = [i[token]]
    return e2e_pdr_per_hop


def merge_dicts_of_arrays(dict1, dict2):
    for i in list(dict2.keys()):
        if i in dict1:
            dict1[i] += (dict2[i])
        else:
            dict1[i] = dict2[i]
    return dict1


if __name__ == '__main__':
    parser = configure_cmd_parser()
    args = parser.parse_args()

    loader = load_yaml(args.filename)

    runs = loader['runs']

    e2e_event_pdr = []
    e2e_report_pdr = []
    e2e_event_pdr_per_hop = {}
    e2e_report_pdr_per_hop = {}

    for run in runs:
        run = add_e2e_pdr_to_node(run, 'event_pdr')
        run = add_e2e_pdr_to_node(run, 'report_pdr')
        e2e_event_pdr += get_run_e2e_pdr(run, 'event_pdr')
        e2e_report_pdr += e2e_report_pdr + get_run_e2e_pdr(run, 'report_pdr')

        e2e_event_pdr_per_hop = merge_dicts_of_arrays(e2e_event_pdr_per_hop,
                                                      get_run_e2e_pdr_per_hop(run, 'event_pdr'))
        e2e_report_pdr_per_hop = merge_dicts_of_arrays(e2e_report_pdr_per_hop,
                                                       get_run_e2e_pdr_per_hop(run, 'report_pdr'))

    header = ''
    data = args.filename
    header += '#e2e event avg.pdr'
    data += '#' + str(np.average(e2e_event_pdr))

    header += '#e2e report avg.pdr'
    data += '#' + str(np.average(e2e_report_pdr))

    e2e_event_pdr_per_hop = dict(sorted(e2e_event_pdr_per_hop.items()))
    e2e_report_pdr_per_hop = dict(sorted(e2e_report_pdr_per_hop.items()))

    for i in list(e2e_event_pdr_per_hop.keys()):
        header += '#hop ' +str(i)+' event pdr'
        data += '#' + str(np.average(e2e_event_pdr_per_hop[i]))

    if args.gap:
        gap = int(args.gap) - len(e2e_event_pdr_per_hop)
        for i in range(0,gap):
            header += ' # '
            data += ' # '

    for i in list(e2e_report_pdr_per_hop.keys()):
        header += '#hop ' +str(i)+' report pdr'
        data += '#' + str(np.average(e2e_report_pdr_per_hop[i]))

    if not args.no_header:
        print(header)
    print(data)

    # print(run['seed'])
#        pdr_arr = list(run['pdr'].values())[1:]
#        run['avg_pdr'] = np.average(pdr_arr)
#        run['std_pdr'] = np.std(pdr_arr)
#        run['disconn'] = pdr_arr.count(0)
#        # print(run['std_pdr'])
#
#        loc_pdr = []
#        for i in run['loc_pdr']:
#            if 'hop' not in i:
#                radio_stat.append({'hop': 0, 'radio': i['radio'], 'pdr': 0})
#            else:
#                radio_stat.append({'hop': i['hop'], 'radio': i['radio'], 'pdr': 0})
#            if run['pdr'][i['node']]:
#                if i['hop'] not in pdr_per_hop_hist:
#                    pdr_per_hop_hist[i['hop']] = [run['pdr'][i['node']]]
#                    path_per_hop_hist[i['hop']] = [len(i['routing_table'])]
#                else:
#                    pdr_per_hop_hist[i['hop']].append(run['pdr'][i['node']])
#                    path_per_hop_hist[i['hop']].append(len(i['routing_table']))
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
#                                    meas=next((item for item in i['rreq_table'] if item['node'] == j['node']), None)
#                                    loc_pdr_per_hop_hist[j['hop']]['meas_pdr'].append(
#                                        meas['ack_count'] / meas['pkt_count'])
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
#        plt.subplot(2, int(np.ceil(len(loc_pdr_per_hop_hist.keys()) / 2)), i+1)
#        plt.hist( [ p-mp for (p, mp) in zip(loc_pdr_per_hop_hist[i]['pdr'], loc_pdr_per_hop_hist[i]['meas_pdr'])], bins)
#        # plt.hist(loc_pdr_per_hop_hist[i]['pdr'], bins)
#        plt.title('Hop:'+str(i))
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
#    plt.tight_layout()
#    pdr_per_hop_hist = dict(sorted(pdr_per_hop_hist.items()))
#    for i in pdr_per_hop_hist:
#        if args.sheet:
#            header += '#e2e.hop.'+str(i)+'.pdr'
#            data += '#' + str(np.average(pdr_per_hop_hist[i]))
#        else:
#            print('Hop '+str(i)+' e2e PDR: '+str(np.average(pdr_per_hop_hist[i])))
#
#    if args.gap:
#        gap = int(args.gap) - len(pdr_per_hop_hist)
#        for i in range(0,gap):
#            header += ' # '
#            data += ' # '
#    path_per_hop_hist = dict(sorted(path_per_hop_hist.items()))
#
#    for i in path_per_hop_hist:
#        if args.sheet:
#            header += '#hop.'+str(i)+'.path'
#            data += '#' + str(np.average(path_per_hop_hist[i]))
#        else:
#            print('Hop '+str(i)+' e2e PDR: '+str(np.average(path_per_hop_hist[i])))
#
#    if not args.data:
#        if args.image:
#            plt.savefig(args.filename.replace('yaml', '_diff.png'), bbox_inches='tight')
#        else:
#            plt.show()
#        plt.close()
#    bins = np.arange(0, 1.1, 0.1)
#    for i in loc_pdr_per_hop_hist:
#        plt.subplot(2, int(np.ceil(len(loc_pdr_per_hop_hist.keys()) / 2)), i+1)
#        plt.hist(loc_pdr_per_hop_hist[i]['pdr'], bins)
#        plt.title('Hop:'+str(i))
#    plt.tight_layout()
#
#    if not args.data:
#        if args.image:
#            plt.savefig(args.filename.replace('yaml', '_pdr.png'), bbox_inches='tight')
#        else:
#            plt.show()
#
#    plt.close()
#    if not args.data:
#        plt.plot(rx_rate)
#        plt.plot(hop_arr)
#        plt.show()
#
#    np_rx = np.array(rx_rate)
#    np_hop = np.array(hop_arr)
#
#    m = np.row_stack((np_rx, np_hop))
#    ret = np.corrcoef(m)
#
#    if args.sheet:
#        if not args.no_header:
#            print(header)
#        print(data)