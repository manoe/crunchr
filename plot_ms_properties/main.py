#!/bin/python3

import argparse
import yaml
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import pandas as pd
import shelve
import os.path
import copy

def shelve_out(filename, keys):
    my_shelf = shelve.open(filename, 'n')  # 'n' for new
    for key in keys:
        #print('key: '+str(key))
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
    my_shelf = shelve.open(filename)
    for key in my_shelf:
        globals()[key] = my_shelf[key]
    my_shelf.close()

# https://matplotlib.org/stable/tutorials/colors/colors.html
def role_to_color(role):
    if role == 'central':
        return 'tab:pink'
    elif role == 'internal':
        return 'tab:brown'
    elif role == 'border':
        return 'tab:cyan'
    elif role == 'external':
        return 'tab:blue'
    return 'tab:grey'


def calc_avg_path_num(run):
    pn_arr = []
    for node in run['loc_pdr']:
        if node['role'] == 'external' and 'routing_table' in node:
            pn_arr.append(len(node['routing_table']))
    return np.average(pn_arr)


def calc_avg_pdr(run):
    dead_nodes = []
    if args.no_dead:
        dead_nodes = [i['node'] for i in run['loc_pdr'] if i['state'] == 'DEAD']
        #print(dead_nodes)
    ring_nodes = []
    if args.external:
        ring_nodes = [i['node'] for i in run['loc_pdr'] if i['role'] != 'external']

    pdr_arr = []
    if args.event:
        pdr_arr = [node['event_pdr'] for node in run['pdr'] if 'event_pdr' in node
                   and node['node'] not in dead_nodes and node['node'] not in ring_nodes]
    else:
        pdr_arr = [node['report_pdr'] for node in run['pdr'] if 'report_pdr' in node
                   and node['node'] not in dead_nodes and node['node'] not in ring_nodes]
    #print(pdr_arr)
    return np.average(pdr_arr)


def construct_graph(run):
    nw = nx.DiGraph()
    for i in run['loc_pdr']:
        nw.add_node(i['node'], role=i['role'], master=i['master'], pos=[i['x'], i['y']], state=i['state'])
        if 'routing_table' in i:
            for j in i['routing_table']:
                if i['role'] == 'external':
                    pathid = [k['pathid'] for k in j['pathid']]
                    secl = False
                    for k in j['pathid']:
                        if k['secl']:
                            secl = True
                    nw.add_edge(i['node'], j['node'], pathid=pathid, secl=secl)
                else:
                    nw.add_edge(i['node'], j['node'], secl=j['secl'])
    return nw

def calc_avg_nw_diameter(run):
    nw = construct_graph(run)
    outers = [node for node, in_degree in nw.in_degree() if in_degree == 0]
    diameters = []
    sinks = [node[0] for node in nx.get_node_attributes(nw,'role').items() if node[1] == 'central']
    for i in outers:
        d = []
        for s in sinks:
            try:
                d.append(nx.shortest_path_length(nw, source=i, target=s))
            except nx.exception.NetworkXNoPath as exp:
                print(exp)
        if len(d) > 0:
            diameters.append(max(d))
    #print('Diameters: ' + str(diameters))
    return np.average(diameters)


def calc_conn_ratio(run):
    if args.no_dead:
        dead_nodes = [i['node'] for i in run['loc_pdr'] if i['state'] == 'DEAD']
        nw = construct_graph(run)
        nw.remove_nodes_from(dead_nodes)
        conn = []
        sinks = [node[0] for node in nx.get_node_attributes(nw, 'role').items() if node[1] == 'central']

        for i in nw.nodes():
            paths = []
            for s in sinks:
                try:
                    paths.append(nx.shortest_path_length(nw, source=i, target=s))
                except nx.exception.NetworkXNoPath as exp:
                    None
                    #print('No path '+str(exp))
            if len(paths) > 0:
                conn.append(i)
        #print(conn)
        #print(len(conn)/len(nw.nodes()))
        return float(len(conn)) / float(len(nw.nodes()))
    else:
        return float(len([n for n in run['loc_pdr'] if n['state'] == 'WORK'])) / float(len(run['loc_pdr']))


def calc_avg_std_distance(run):
    nw = construct_graph(run)
    d = [np.linalg.norm(np.subtract(nx.get_node_attributes(nw, 'pos')[edge[0]],
                                    nx.get_node_attributes(nw, 'pos')[edge[1]]))
         for edge in nw.edges]
    #print('pos arr: '+ str(d))
    #print('std:'+str(np.std(d)))
    return np.average(d), np.std(d)


def to_color(p, th=0.6):
    if p < th:
        return 0.7
    if p >= th:
        return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_ms_properties', description='Plot bar charts, yeah', epilog=':-(')
    parser.add_argument('-px', '--param-x', dest='param_x', action='store', nargs='+', type=float)
    parser.add_argument('-d', '--no_dead', dest='no_dead', action='store_true')
    parser.add_argument('-e', '--event', dest='event', action='store_true')
    parser.add_argument('-ex', '--external', dest='external', action='store_true')
    parser.add_argument('-tx', '--title-x', dest='title_x', action='store', type=str, default='X')
    parser.add_argument('-ty', '--title-y', dest='title_y', action='store', type=str, default='Y')
    parser.add_argument('-t', '--tail', dest='tail', action='store', type=int)
    parser.add_argument('-tt', '--tail-target', dest='tail_target', action='store', type=str, default='pdr')
    parser.add_argument('-f', '--file', dest='file', help='use the pattern blabla_px.yaml')
    args = parser.parse_args()

    if False:
        print('nothing')
    #if os.path.isfile(args.file):
    #    print('Shelved file present, reading in')
    #    shelve_in(args.file)
    else:
        # arr [row][column] - inner = column, outer = row
        pdr_arr = [[] for x in args.param_x]
        # average path number
        apn_arr = [[] for x in args.param_x]
        # average network diameter
        and_arr = [[] for x in args.param_x]
        # ratio of connected nodes
        con_arr = [[] for x in args.param_x]
        # avg. Euclidian distance
        aed_arr = [[] for x in args.param_x]
        # std. Euclidian distance
        sed_arr = [[] for x in args.param_x]

        for idx_q, q in enumerate(args.param_x):
            filename = args.file.replace('px', '{:.3f}'.format(q))
            print('Opening file: ' + filename)
            loader = yaml.safe_load(open(filename, 'r'))

            for r_idx, run in enumerate(loader['runs']):
                if 'pdr' in run and 'loc_pdr' in run:
                    pdr_arr[idx_q].append(calc_avg_pdr(run))
                    apn_arr[idx_q].append(calc_avg_path_num(run))
                    and_arr[idx_q].append(calc_avg_nw_diameter(run))
                    con_arr[idx_q].append(calc_conn_ratio(run))
                    aed, sed = calc_avg_std_distance(run)
                    aed_arr[idx_q].append(aed)
                    sed_arr[idx_q].append(sed)

        def avg_arr(arr):
            return [np.average(arr[idx_q]) for idx_q, q in enumerate(args.param_x)]

        def select_tail(pdr_arr, apn_arr, and_arr, con_arr, aed_arr, sed_arr):
            if args.tail_target == 'pdr':
                for idx,i in enumerate(pdr_arr):
                    pdr_arr[idx], apn_arr[idx], and_arr[idx], con_arr[idx], aed_arr[idx], sed_arr[idx] = (list(t) for t in zip(*sorted(zip(pdr_arr[idx], apn_arr[idx], and_arr[idx], con_arr[idx], aed_arr[idx], sed_arr[idx]), reverse=True)))
                    pdr_arr[idx] = pdr_arr[idx][:args.tail]
                    apn_arr[idx] = apn_arr[idx][:args.tail]
                    and_arr[idx] = and_arr[idx][:args.tail]
                    con_arr[idx] = con_arr[idx][:args.tail]
                    aed_arr[idx] = aed_arr[idx][:args.tail]
                    sed_arr[idx] = sed_arr[idx][:args.tail]


        if args.tail:
            select_tail(pdr_arr, apn_arr, and_arr, con_arr, aed_arr, sed_arr)

        #print('PDR arr: '+str(pdr_arr))
        avg_apn_arr = avg_arr(apn_arr)
        avg_and_arr = avg_arr(and_arr)
        avg_pdr_arr = avg_arr(pdr_arr)
        avg_con_arr = avg_arr(con_arr)
        avg_aed_arr = avg_arr(aed_arr)
        avg_sed_arr = avg_arr(sed_arr)

        #print(con_arr)
        #print('Shelving out data')
        shelve_out(args.file, ['avg_apn_arr','avg_and_arr','avg_pdr_arr','avg_con_arr','avg_aed_arr', 'avg_sed_arr'])

    # https://matplotlib.org/stable/gallery/images_contours_and_fields/image_annotated_heatmap.html

    fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(5, 5))
    plt.subplots_adjust(wspace=0.1, hspace=0.1)

    ax = axs.ravel()

    for idx, arr in enumerate([avg_pdr_arr, avg_apn_arr, avg_and_arr, avg_con_arr, avg_aed_arr, avg_sed_arr]):
    # Show all ticks and label them with the respective list entries
        ax[idx].bar(np.arange(len(args.param_x)), arr)
        #colours = im.cmap(im.norm(arr))
        #print(colours)
        #image = arr
        ax[idx].set_xticks(np.arange(len(args.param_x)), labels=args.param_x)

        ax[idx].set_xlabel(r"{}".format(args.title_x))
        ax[idx].set_ylabel(r"{}".format(args.title_y))

    # Rotate the tick labels and set their alignment.
        plt.setp(ax[idx].get_xticklabels(), rotation=45, ha="right",
                 rotation_mode="anchor")


    for idx, label in enumerate(['Average Network PDR', 'Average Path Number', 'Average Network Diameter', 'Average Connected Node Ratio', 'Average Euclidian distance', 'Average Euclidian distance std']):
        ax[idx].set_title(label, fontsize='small')
    fig.tight_layout()
    #plt.show()

    bigarr = []
    for i in [pdr_arr, aed_arr, sed_arr]:
        bigarr.append(list(np.array(i).flat))
    bigarr = list(np.array(bigarr).flat)
    bigarr2d = np.reshape(bigarr, (3,len(np.array(pdr_arr).flat)))
    #print(list(bigarr2d))
    corrm = np.corrcoef(bigarr2d)
    cols = ['PDR', 'E(D)', 'D(D)']
    df = pd.DataFrame(corrm, columns=cols, index=cols)
    print(df)
