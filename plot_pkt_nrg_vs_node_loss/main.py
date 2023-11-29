#!/bin/python3
import math
import yaml
import argparse
import statistics
import matplotlib.pyplot as plt
import numpy as np

def calc_data_whatever(actual, prev, node_list):
    sum_nrg = 0
    sum_sent_pkt = 0
    sum_recv_pkt = 0
    for idx, i in enumerate(actual['nodes']):
        if i['energy'] == 0:
            raise RuntimeError("Energy is 0, cannot calculate proper result")

        sum_nrg += prev['nodes'][idx]['energy'] - i['energy']
        if i in node_list:
            sum_sent_pkt += i['report_sent'] - prev['nodes'][idx]['report_sent']
            sum_recv_pkt += i['report_recv'] - prev['nodes'][idx]['report_recv']
    if sum_recv_pkt == 0:
        return 0
    return sum_nrg / sum_recv_pkt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_pkt_nrg_vs_node_loss',
                                     description='Plot nrg spent on packets versus node loss over time', epilog=':-(')
    parser.add_argument('-t', '--time', action='store', dest='time', default=1800, type=int)
    parser.add_argument('-H', '--hop', action='store', dest='hop', default=3, type=int)
    parser.add_argument('-n', '--node', action='store', dest='node', default=2, type=int)
    parser.add_argument('-e', '--energy', action='store', dest='energy', default=18720, type=float)
    parser.add_argument('-f', '--filename', help='filenames', nargs='+', required=True, dest='files')

    args = parser.parse_args()
    y_nrg = {}

    for file in args.files:
        stream = open(file, 'r')
        loader = yaml.safe_load(stream)
        y_raw_nrg = {}

        node_file = file
        node_file.replace('nrg', 'pdr')
        node_stream = open(node_file, 'r')
        node_loader = yaml.safe_load(node_stream)

        node_idx = 0

        for i in loader['runs']:
            nodes = [i['node'] for i in node_loader['runs'][node_idx]['loc_pdr'] if i['hop'] > args.hop]
            node_idx += 1

            y_data = {}
            block = 1
            prev_data = 0
            for idx, j in enumerate(i['nrg_list']):
                if j['timestamp'] > args.time*block:
                    y_data[block-1] = calc_data_whatever(j, i['nrg_list'][prev_data], nodes)
                    block += 1
                    prev_data = idx
                    print(str(j['timestamp'])+' '+str(block))
            y_data[block] = calc_data_whatever(i['nrg_list'][-1], i['nrg_list'][prev_data])
            print('Last : '+str(i['nrg_list'][-1]['timestamp'])+' block: '+str(block))

            for i in y_data.keys():
                if i in y_raw_nrg:
                    y_raw_nrg[i].append(y_data[i])
                else:
                    y_raw_nrg[i] = [y_data[i]]

        y_nrg[file] = [statistics.mean(x) for x in y_raw_nrg.values()]
        x = list(y_raw_nrg.keys())
        print(y_nrg[file])

    for i in y_nrg.values():
        plt.plot(x, i)
    plt.legend([str(x).split('/')[-1] for x in y_nrg.keys()])
    plt.show()
