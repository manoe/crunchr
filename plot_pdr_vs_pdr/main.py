#!/bin/env python3

import matplotlib.pyplot as plt
import yaml
import argparse

def collect_pdr(run):
    pdr_dict = {i['node']: i['pdr'] for i in run['pdr'] if 'pdr' in i}
    return list(dict(sorted(pdr_dict.items())).values())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_pdr_vs_pdr', description='Plot PDR versus PDR, yeah', epilog=':-(')
    parser.add_argument('-fx', '--file-x', dest='file_x', action='store', type=str, required=True)
    parser.add_argument('-fy', '--file-y', dest='file_y', action='store', type=str, required=True)
    parser.add_argument('-tx', '--title-x', dest='title_x', action='store', type=str, default='X')
    parser.add_argument('-ty', '--title-y', dest='title_y', action='store', type=str, default='Y')
    args = parser.parse_args()

    x_data = collect_pdr(yaml.safe_load(open(args.file_x, 'r'))['runs'][0])
    y_data = collect_pdr(yaml.safe_load(open(args.file_y, 'r'))['runs'][0])

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(4, 4))
    plt.subplots_adjust(wspace=0.1, hspace=0.1)
    ax.plot(x_data, y_data)
    ax.set_xlabel(args.title_x)
    ax.set_ylabel(args.title_y)
    plt.show()
