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

def collect_node_pdr(run):
    return {node['node']: node['report_pdr'] for node in run['pdr'] if 'report_pdr' in node}

def calc_pdr(run):
    pdrs = []
    for node in run['pdr']:
        if 'report_pdr' in node:
            pdrs.append(node['report_pdr'])
    return np.average(pdrs)


def gen_node_loc(run):
    return {i['node']: [i['x'], i['y']] for i in run['loc_pdr']}


def gen_node_pdr(run):
    return {i['node']: i['report_pdr'] for i in run['pdr'] if 'report_pdr' in i}


def calc_dc_pdr(run):
    loc = gen_node_loc(run)
    pdr = gen_node_pdr(run)
    d_max = max([np.linalg.norm(i) for i in loc.values()])
    return np.average([np.linalg.norm(loc[i])/d_max*pdr[i] for i in pdr.keys()])


def coll_d_p(run):
    loc = gen_node_loc(run)
    pdr = gen_node_pdr(run)
    d_max = max([np.linalg.norm(i) for i in loc.values()])
    return [[np.linalg.norm(loc[i]) / d_max for i in pdr.keys()], [pdr[i] for i in pdr.keys()]]


def calc_connr(run):
    return len([node['node'] for node in run['pdr'] if 'report_pdr' in node and node['report_pdr'] != 0])/len([node['node'] for node in run['pdr'] if 'report_pdr' in node])


def tail(arr, th):
    return len([i for i in arr if i >= th])/len(arr)


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
    parser.add_argument('-p', '--plot', dest='plot', action='store', choices=['pdr', 'connr', 'dc_pdr', 'd_p'], help='Kind of the plot')
    parser.add_argument('-s', '--shelve', dest='shelve', action='store_true', help='use the pattern blabla_px_py_babla.yaml')
    args = parser.parse_args()

    arr_pdr = []
    arr_connr = []
    arr_dc_pdr = []
    arr_d_p = []
    arr_reg = []

    if args.shelve:
        shelve_in(args.file)
    else:
        for idx_q, q in enumerate(args.param_x):
            y_pdr_arr = []
            y_connr_arr = []
            y_dc_pdr_arr = []
            y_d_p_arr = []
            y_reg_arr = []
            for idx_p, p in enumerate(args.param_y):
                filename = args.file.replace('px', q).replace('py', p)
                print('Opening file: ' + filename)
                loader = yaml.safe_load(open(filename, 'r'))
                y_pdr_arr.append([calc_pdr(run) for run in loader['runs']])
                y_connr_arr.append([calc_connr(run) for run in loader['runs']])
                y_dc_pdr_arr.append([calc_dc_pdr(run) for run in loader['runs']])
                d_p_arr = [[], []]
                reg_arr = []
                for run in loader['runs']:
                    arr = coll_d_p(run)
                    d_p_arr[0] += arr[0]
                    d_p_arr[1] += arr[1]
                    reg_arr.append(np.linalg.lstsq(np.vstack([arr[0], np.ones(len(arr[0]))]).T, arr[1], rcond=None)[0])
                print('d_p_arr len: '+str(len(d_p_arr)))
                y_d_p_arr.append(d_p_arr)
                y_reg_arr.append(reg_arr)
            arr_pdr.append(y_pdr_arr)
            arr_connr.append(y_connr_arr)
            arr_dc_pdr.append(y_dc_pdr_arr)
            arr_d_p.append(y_d_p_arr)
            arr_reg.append(y_reg_arr)

        shelve_out(args.file, ['arr_pdr', 'arr_connr', 'arr_dc_pdr', 'arr_d_p', 'arr_reg'])

    if 'd_p' == args.plot:
        fig, axs = plt.subplots(nrows=len(args.param_x), ncols=len(args.param_y), figsize=(3*len(args.param_y), 3*len(args.param_x)))
        plt.subplots_adjust(wspace=0.1, hspace=0.1)
        ax = axs.ravel()
        print(arr_d_p)
        for idx_q, q in enumerate(args.param_x):
            for idx_p, p in enumerate(args.param_y):
                ax[len(args.param_y)*idx_q+idx_p].set_title(str(q)+', '+str(p))
                ax[len(args.param_y)*idx_q+idx_p].scatter(arr_d_p[idx_q][idx_p][0], arr_d_p[idx_q][idx_p][1])
                #reg=np.linalg.lstsq(arr_d_p[idx_q][idx_p][0], arr_d_p[idx_q][idx_p][1], rcond=None)[0]
                reg = np.linalg.lstsq(np.vstack([arr_d_p[idx_q][idx_p][0], np.ones(len(arr_d_p[idx_q][idx_p][0]))]).T, arr_d_p[idx_q][idx_p][1], rcond=None)[0]
        plt.show()
        print(arr_d_p)
        exit(0)

    arr_pdr_tailed = [[tail(i, args.tail) for i in j] for j in arr_pdr]
    arr_connr_tailed = [[tail(i, args.tail) for i in j] for j in arr_connr]
    arr_dc_pdr_tailed = [[tail(i, args.tail) for i in j] for j in arr_dc_pdr]

    df_pdr = pd.DataFrame(arr_pdr_tailed, columns=args.param_y, index=args.param_x)
    df_connr = pd.DataFrame(arr_connr_tailed, columns=args.param_y, index=args.param_x)
    df_dc_pdr = pd.DataFrame(arr_dc_pdr_tailed, columns=args.param_y, index=args.param_x)
    print('PDRs with tail set to '+str(args.tail))
    print(df_pdr.to_string())
    print('Connection ratio with tail set to '+str(args.tail))
    print(df_connr.to_string())
    print('Distance corrected PDR with tail set to ' + str(args.tail))
    print(df_dc_pdr.to_string())

    if args.plot is None:
        exit(0)

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(4, 4))
    plt.subplots_adjust(wspace=0.1, hspace=0.1)

    if 'pdr' == args.plot:
        img = arr_pdr_tailed
        ax.set_title('PDR with tail='+str(args.tail))
    elif 'connr' == args.plot:
        img = arr_connr_tailed
        ax.set_title('Connection ratio with tail=' + str(args.tail))
    elif 'dc_pdr' == args.plot:
        img = arr_dc_pdr_tailed
        ax.set_title('Distance corrected PDR with tail=' + str(args.tail))
    else:
        print('Error, unknown plot source')
        exit(-1)

    ax.imshow(img)
    for i in range(len(args.param_x)):
        for j in range(len(args.param_y)):
            text = ax.text(j, i, "{:.3f}".format(img[i][j]), ha="center", va="center", fontsize='small')

    ax.set_xticks(np.arange(len(args.param_y)), labels=args.param_y)
    ax.set_yticks(np.arange(len(args.param_x)), labels=args.param_x)
    ax.set_xlabel(r"{}".format(args.title_y))
    ax.set_ylabel(r"{}".format(args.title_x))

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    fig.tight_layout()
    plt.show()
