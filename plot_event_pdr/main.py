#!/bin/python3

import argparse
import yaml
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_event_pdr', description='Plot event PDR specific to some nodes', epilog=':-(')
    parser.add_argument('-n', '--nodes', dest='nodes', action='store', nargs='+', type=int)
    parser.add_argument('-f', '--files', dest='files', action='store', nargs='+', type=str)
    parser.add_argument('-l', '--labels', dest='labels', action='store', nargs='+', type=str)
    parser.add_argument('-b', '--base-files', dest='base_files', action='store', nargs='+', type=str)

    args = parser.parse_args()

    event_pdr = {file: {node: [] for node in args.nodes} for file in args.files}

    for file in args.files:
        loader = yaml.safe_load(open(file, 'r'))
        for run in loader['runs']:
            for node in run['pdr']:
                if node['node'] in args.nodes and 'event_pdr' in node:
                    event_pdr[file][node['node']].append(node['event_pdr'])

    for file in event_pdr.keys():
        for node in event_pdr[file].keys():
            event_pdr[file][node] = np.average(event_pdr[file][node])

    report_pdr = {file: {node: [] for node in args.nodes} for file in args.base_files}
    for file in args.base_files:
        loader = yaml.safe_load(open(file, 'r'))
        for run in loader['runs']:
            for node in run['pdr']:
                if node['node'] in args.nodes and 'report_pdr' in node:
                    report_pdr[file][node['node']].append(node['report_pdr'])

    for file in report_pdr.keys():
        for node in report_pdr[file].keys():
            report_pdr[file][node] = np.average(report_pdr[file][node])

    diff_pdr = {file: {node: [] for node in args.nodes} for file in args.files}

    for file in report_pdr.keys():
        for node in report_pdr[file].keys():
            diff_pdr[file][node] = -(report_pdr[file][node] - event_pdr[file][node]) / report_pdr[file][node] * 100

    width = 0.8
    bar_width = width / len(args.files)

    plt.figure(figsize=(10, 5))
    plt.ylim([0, 0.85])

    ax = plt.subplot(211)
    ax.set_ylim([0, 0.8])
    colors = []
    for idx, i in enumerate(event_pdr):
        bc = plt.bar([x + idx*bar_width-width/2 for x in range(len(args.nodes))], list(event_pdr[i].values()), bar_width)
        plt.bar_label(bc, label=args.files, fmt='%.2f', rotation=45, fontsize='small')
        colors.append(bc.patches[0].get_facecolor())

    for idx, i in enumerate(event_pdr):
        plt.axhline(y=np.average(list(event_pdr[i].values())), color=colors[idx], linestyle='-') # label=str(np.average(list(event_pdr[i].values())))
        s = str(np.average(list(event_pdr[i].values()))).format('%.2f')
        txt = '{an:.2f}'
        plt.text(-1, np.average(list(event_pdr[i].values())), txt.format(an=np.average(list(event_pdr[i].values()))), fontsize='small', rotation=45)
    plt.grid(axis='y')
    plt.ylabel('Event PDR')
    plt.xlabel('Nodes')
    plt.xticks(range(len(args.nodes)), labels=args.nodes)
    plt.title('(a)', loc='left')
    if args.labels is not None:
        plt.legend(list(args.labels))
    else:
        plt.legend(list(event_pdr.keys()))

    ax = plt.subplot(212)

    for idx, i in enumerate(diff_pdr):
        bc = plt.bar([x + idx*bar_width-width/2 for x in range(len(args.nodes))], list(diff_pdr[i].values()), bar_width)
        plt.bar_label(bc, label=args.files, fmt='%.0f%%', rotation=-45, fontsize='small')
        colors.append(bc.patches[0].get_facecolor())

    for idx, i in enumerate(diff_pdr):
        plt.axhline(y=np.average(list(diff_pdr[i].values())), color=colors[idx], linestyle='-.') # label=str(np.average(list(event_pdr[i].values())))
        s = str(np.average(list(diff_pdr[i].values()))).format('%.0f%%')
        txt = '{an:.0f}%'
        plt.text(-1, np.average(list(diff_pdr[i].values())), txt.format(an=np.average(list(diff_pdr[i].values()))), fontsize='small', rotation=-45)
    plt.grid(axis='y')
    plt.ylabel('Difference in PDR')
    plt.xlabel('Nodes')
    plt.xticks(range(len(args.nodes)), labels=args.nodes)
    plt.title('(b)', loc='left')

    ax.set_ylim([-110, 0])
    plt.tight_layout()
    plt.show()
