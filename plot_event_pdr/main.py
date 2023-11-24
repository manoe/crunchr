#!/bin/python3

import argparse
import yaml
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_event_pdr', description='Plot event PDR specific to some nodes', epilog=':-(')
    parser.add_argument('-n', '--nodes', dest='nodes', action='store', nargs='+', type=int)
    parser.add_argument('-f', '--files', dest='files', action='store', nargs='+', type=str)

    args = parser.parse_args()

    event_pdr = {file: {node: [] for node in args.nodes} for file in args.files}

    for file in args.files:
        loader = yaml.safe_load(open(file, 'r'))
        for run in loader['runs']:
            for node in run['pdr']:
                if node['node'] in args.nodes:
                    event_pdr[file][node['node']].append(node['event_pdr'])

    for file in event_pdr.keys():
        for node in event_pdr[file].keys():
            event_pdr[file][node] = np.average(event_pdr[file][node])

    width = 0.8
    bar_width = width / len(args.files)

    colors = []
    for idx, i in enumerate(event_pdr):
        bc = plt.bar([x + idx*bar_width-width/2 for x in range(len(args.nodes))], list(event_pdr[i].values()), bar_width)
        plt.bar_label(bc, label=args.files, fmt='%.2f')
        colors.append(bc.patches[0].get_facecolor())

    for idx, i in enumerate(event_pdr):
        plt.axhline(y=np.average(list(event_pdr[i].values())), color=colors[idx], linestyle='-')

    plt.title('Event PDR')
    plt.xticks(range(len(args.nodes)), labels=args.nodes)

    plt.legend(list(event_pdr.keys()))
    plt.show()
