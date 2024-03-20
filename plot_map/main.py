import argparse

import matplotlib
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import yaml
import pandas as pd

def calc_pdr(run):
    pdrs = []
    for node in run['pdr']:
        if 'report_pdr' in node:
            pdrs.append(node['report_pdr'])
    return np.average(pdrs)


def tail(arr, th):
    return len([i for i in arr if i > th])/len(arr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_map', description='Plot map, yeah', epilog=':-(')
    parser.add_argument('-px', '--param-x', dest='param_x', action='store', nargs='+', type=str)
    parser.add_argument('-py', '--param-y', dest='param_y', action='store', nargs='+', type=str)
    parser.add_argument('-x', '--exclude', dest='exclude', nargs='+', type=int, help='Exclude nodes from calculation')
    parser.add_argument('-i', '--include', dest='include', nargs='+', type=int, help='Include only these nodes in calculation')
    parser.add_argument('-d', '--no_dead', dest='no_dead', action='store_true')
    parser.add_argument('-ex', '--external', dest='external', action='store_true')
    parser.add_argument('-e', '--event', dest='event', action='store_true')
    parser.add_argument('-tx', '--title-x', dest='title_x', action='store', type=str, default='X')
    parser.add_argument('-ty', '--title-y', dest='title_y', action='store', type=str, default='Y')
    parser.add_argument('-f', '--file', dest='file', help='use the pattern blabla_px_py_babla.yaml')
    parser.add_argument('-t', '--tail', dest='tail', action='store', type=float, help='The tail threshold')
    args = parser.parse_args()

    arr = []

    for idx_q, q in enumerate(args.param_x):
        y_arr = []
        for idx_p, p in enumerate(args.param_y):
            filename = args.file.replace('px', q).replace('py', p)
            print('Opening file: ' + filename)
            loader = yaml.safe_load(open(filename, 'r'))
            y_arr.append(tail([calc_pdr(run) for run in loader['runs']], args.tail))
        arr.append(y_arr)

    df = pd.DataFrame(arr, columns=args.param_x, index=args.param_y)
    print(df.to_string())
