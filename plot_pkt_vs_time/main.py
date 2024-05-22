#!/bin/python3

import math
import yaml
import argparse
import matplotlib.pyplot as plt
import sys
import numpy as np
import matplotlib.patches as mpatches

def sum_list_prop(list_prop, attr_value=None):
    if attr_value is None:
        return [sum([x[list_prop] for x in i['nodes']]) for i in loader['nrg_list']]
    else:
        return [len([x[list_prop] for x in i['nodes'] if x[list_prop] == attr_value]) for i in loader['nrg_list']]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_pdr_nrg', description='Plot network pdr and energy over time', epilog=':-(')
    parser.add_argument('-f', dest='filename', help='use ``-\'\' for stdin', nargs='+')
    parser.add_argument('-dc', dest='dead_node_count', action='store_true')
    parser.add_argument('-e', '--event', dest='event', type=int, nargs='+')

    args = parser.parse_args()

    files = args.filename

    sent_report_pkt = {}
    recv_report_pkt = {}
    dead_node_count = {}
    timestamp = {}

    for file in files:
        stream = open(file, 'r')

        loader = yaml.safe_load(stream)

        sum_sent_report = sum_list_prop('report_sent')
        sum_recv_report = sum_list_prop('report_recv')

        if args.dead_node_count:
            dead_node_count[file] = sum_list_prop('state', 'dead')

        sent_report_pkt[file] = np.subtract(sum_sent_report[1:], sum_sent_report[:-1])
        recv_report_pkt[file] = np.subtract(sum_recv_report[1:], sum_recv_report[:-1])

        timestamp[file] = [round(i['timestamp'], 0) for i in loader['nrg_list']][:-1]

    rows = 2 if len(files) > 1 else 1
    columns = math.ceil(len(files)/2)

    max_val = max([i.max() for i in sent_report_pkt.values()])
    min_val = min([i.min() for i in recv_report_pkt.values()])

    colors = []

#    fig, ax = plt.subplots(nrows=rows, ncols=columns)
    for idx, file in enumerate(files):
        fig, ax = plt.subplots(nrows=rows, ncols=columns, num=idx)
        line1 = ax.plot(timestamp[file], np.transpose(np.array([sent_report_pkt[file], recv_report_pkt[file]])))
        ax.set_ylabel('Pkt/s')
        ax.set_xlabel('Time (sec)')
        colors = [i.get_color() for i in line1]

#        ax.legend(['Sent pkt', 'Recv pkt'])
        plt.ylim(top=math.ceil(max_val/10.0)*10.0, bottom=math.floor(min_val))
        if args.event is not None:
            for i in args.event:
                ax.axvline(x=i, color='r', label='_nolegend_')
        plt.grid(True)
        if args.dead_node_count:
            ax2 = ax.twinx()
            line2 = ax2.plot(timestamp[file], dead_node_count[file][0:-1], color='tab:cyan', label='Dead nodes')
            colors.append(line2[0].get_color())
            ax2.set_ylabel('Node count')
        plt.title(file.split('/')[-1])
        plt.xlim([0, timestamp[file][-1]])
        plt.ylim(bottom=0)
 #   plt.figlegend([line2], ['Line2'])

    labels = ['Sent message', 'Received message', 'Dead node']
    patches = []
    for idx, i in enumerate(colors):
        patches.append(mpatches.Patch(color=i, label=labels[idx]))
    ax.legend(handles=patches)

    plt.tight_layout()
    plt.show()

