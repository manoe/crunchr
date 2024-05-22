#!/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import yaml
import argparse
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.cm as cm
def collect_pdr(run):
    pdr_dict = {i['node']: i['report_pdr'] for i in run['pdr'] if 'report_pdr' in i}
    pdr_ord_dict = dict(sorted(pdr_dict.items()))
    return list(pdr_ord_dict.values()), list(pdr_ord_dict.keys())


def collect_distance(run):
    coord_dict = {i['node']: [i['x'], i['y']] for i in run['loc_pdr']}
    coord_ord_list = list(dict(sorted(coord_dict.items())).values())
    pdr_ord_dict_wo_sink = coord_ord_list[1:]
    d_arr = [np.linalg.norm(i) for i in pdr_ord_dict_wo_sink]
    return [i/max(d_arr) for i in d_arr]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_pdr_vs_pdr', description='Plot PDR versus PDR, yeah', epilog=':-(')
    parser.add_argument('-fx', '--file-x', dest='file_x', action='store', type=str, required=True)
    parser.add_argument('-fy', '--file-y', dest='file_y', action='store', type=str, required=True)
    parser.add_argument('-tx', '--title-x', dest='title_x', action='store', type=str, default='X')
    parser.add_argument('-ty', '--title-y', dest='title_y', action='store', type=str, default='Y')
    args = parser.parse_args()

    x_run = yaml.safe_load(open(args.file_x, 'r'))

    x_data, n_data = collect_pdr(yaml.safe_load(open(args.file_x, 'r'))['runs'][0])
    y_data, n_data = collect_pdr(yaml.safe_load(open(args.file_y, 'r'))['runs'][0])

    d_data = collect_distance(yaml.safe_load(open(args.file_y, 'r'))['runs'][0])

    linear_data = np.arange(0, 1.1, 0.1)
    print(np.average(x_data))
    print(np.average(y_data))

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(4.8, 4))
    plt.subplots_adjust(wspace=0.1, hspace=0.1)
    print(d_data)

    ax.scatter(x_data, y_data, s=80, c=d_data)
    ax.plot(linear_data, linear_data, '--')
    ax.grid()

    #for i, txt in enumerate(n_data):
    #    ax.annotate(txt, (x_data[i], y_data[i]))

    ax.set_xlabel(args.title_x)
    ax.set_ylabel(args.title_y)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)

    plt.colorbar(cm.ScalarMappable(cmap='viridis'), cax=cax, label='Relative distance from sink')
    plt.tight_layout()
    plt.show()
