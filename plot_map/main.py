#!/bin/env python3

import argparse

import matplotlib
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import yaml
import pandas as pd
import shelve as sh

def shelve_out(filename, keys):
    my_shelf = sh.open(filename, 'n')  # 'n' for new
    for key in keys:
        try:
            my_shelf[key] = globals()[key]
        except TypeError:
            #
            # __builtins__, my_shelf, and imported modules can not be shelved.
            #
            print('ERROR shelving: {0}'.format(key))
        except KeyError:
            print('ERROR shelving: {0}'.format(key))
        except:
            print('ERROR')
    my_shelf.close()


def shelve_in(filename):
    my_shelf = sh.open(filename)
    for key in my_shelf:
        globals()[key] = my_shelf[key]
    my_shelf.close()


def calc_pdr(run):
    pdrs = []
    for node in run['pdr']:
        if 'report_pdr' in node:
            pdrs.append(node['report_pdr'])
    return np.average(pdrs)


def calc_connr(run):
    return len([node['node'] for node in run['pdr'] if 'report_pdr' in node and node['report_pdr'] != 0])/len([node['node'] for node in run['pdr'] if 'report_pdr' in node])

def tail(arr, th):
    return len([i for i in arr if i > th])/len(arr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_map', description='Plot map, yeah', epilog=':-(')
    parser.add_argument('-px', '--param-x', dest='param_x', action='store', nargs='+', type=str, required=True)
    parser.add_argument('-py', '--param-y', dest='param_y', action='store', nargs='+', type=str, required=True)
    parser.add_argument('-x', '--exclude', dest='exclude', nargs='+', type=int, help='Exclude nodes from calculation')
    parser.add_argument('-i', '--include', dest='include', nargs='+', type=int, help='Include only these nodes in calculation')
    parser.add_argument('-d', '--no_dead', dest='no_dead', action='store_true')
    parser.add_argument('-ex', '--external', dest='external', action='store_true')
    parser.add_argument('-e', '--event', dest='event', action='store_true')
    parser.add_argument('-tx', '--title-x', dest='title_x', action='store', type=str, default='X')
    parser.add_argument('-ty', '--title-y', dest='title_y', action='store', type=str, default='Y')
    parser.add_argument('-f', '--file', dest='file', help='use the pattern blabla_px_py_babla.yaml', required=True)
    parser.add_argument('-t', '--tail', dest='tail', action='store', type=float, help='The tail threshold', default=0.0)
    parser.add_argument('-s', '--shelve', dest='shelve', action='store_true', help='use the pattern blabla_px_py_babla.yaml')
    args = parser.parse_args()

    arr_pdr = []
    arr_connr = []

    if args.shelve:
        shelve_in(args.file)
    else:
        for idx_q, q in enumerate(args.param_x):
            y_pdr_arr = []
            y_connr_arr = []
            for idx_p, p in enumerate(args.param_y):
                filename = args.file.replace('px', q).replace('py', p)
                print('Opening file: ' + filename)
                loader = yaml.safe_load(open(filename, 'r'))
                y_pdr_arr.append([calc_pdr(run) for run in loader['runs']])
                y_connr_arr.append([calc_connr(run) for run in loader['runs']])
            arr_pdr.append(y_pdr_arr)
            arr_connr.append(y_connr_arr)
        shelve_out(args.file, ['arr_pdr', 'arr_connr'])

    arr_pdr_tailed = [[tail(i, args.tail) for i in j] for j in arr_pdr]
    arr_connr_tailed = [[tail(i, args.tail) for i in j] for j in arr_connr]

    df_pdr = pd.DataFrame(arr_pdr_tailed, columns=args.param_y, index=args.param_x)
    df_connr = pd.DataFrame(arr_connr_tailed, columns=args.param_y, index=args.param_x)
    print('PDRs with tail set to '+str(args.tail))
    print(df_pdr.to_string())
    print('\n')
    print('Connection ratio with tail set to '+str(args.tail))
    print(df_connr.to_string())


