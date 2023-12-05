#!/bin/python3

import argparse
import yaml
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx


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
        print(dead_nodes)
    ring_nodes = []
    if args.external:
        ring_nodes = [i['node'] for i in run['loc_pdr'] if i['role'] != 'external']

    pdr_arr = []
    if args.event:
        pdr_arr = [node['event_pdr'] for node in run['pdr'] if 'event_pdr' in node
                   and node['node'] not in dead_nodes and check_node_wl(node['node']) and node['node'] not in ring_nodes]
    else:
        pdr_arr = [node['report_pdr'] for node in run['pdr'] if 'report_pdr' in node
                   and node['node'] not in dead_nodes and check_node_wl(node['node']) and node['node'] not in ring_nodes]
    print(pdr_arr)
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
    for i in outers:
        try:
            diameters.append(nx.shortest_path_length(nw, source=i, target=0))
        except nx.exception.NetworkXNoPath as exp:
            print(exp)

    return np.average(diameters)


def calc_conn_ratio(run):
    if args.no_dead:
        dead_nodes = [i['node'] for i in run['loc_pdr'] if i['state'] == 'DEAD']
        nw = construct_graph(run)
        nw.remove_nodes_from(dead_nodes)
        conn = []
        for i in nw.nodes():
            try:
                conn.append(nx.shortest_path_length(nw, source=i, target=0))
            except nx.exception.NetworkXNoPath as exp:
                print('No path '+str(exp))
        print(len(conn)/len(nw.nodes()))
        return float(len(conn)) / float(len(nw.nodes()))
    else:
        return float(len([n for n in run['loc_pdr'] if n['state'] == 'WORK'])) / float(len(run['loc_pdr']))

def check_node_wl(node):
    if args.include is None:
        return True
    else:
        return node in args.include

def calc_avg_pdr_from_nrg(run):
    if args.event:
        pkt = 'event_'
    else:
        pkt = 'report_'

    f_arr = [{'node': i['node'], 'sent': i[pkt+str('sent')], 'recv': i[pkt+str('recv')]} for i in run['nrg_list'][-1]['nodes'] if check_node_wl(i['node'])]
    s_arr = []
    for i in run['nrg_list']:
        if len([j['node'] for j in i['nodes'] if j['state'] == 'dead']) > 0:
            s_arr = [{'node': k['node'], 'sent': k[pkt+str('sent')], 'recv': k[pkt+str('recv')]} for k in i['nodes'] if check_node_wl(k['node'])]
            break

    arr = []
    for idx, f in enumerate(f_arr):
        if f_arr[idx]['node'] == s_arr[idx]['node']:
            if f['recv'] - s_arr[idx]['recv'] > 0:
                arr.append((f['recv'] - s_arr[idx]['recv'])/(f['recv'] - s_arr[idx]['recv']))
            else:
                arr.append(0)
        else:
            raise RuntimeError('Indexing out of sync')

    return np.average(arr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_two_parameter_heatmap', description='Plot heatmaps, yeah', epilog=':-(')
    parser.add_argument('-px', '--param-x', dest='param_x', action='store', nargs='+', type=float)
    parser.add_argument('-py', '--param-y', dest='param_y', action='store', nargs='+', type=str)
    parser.add_argument('-x', '--exclude', dest='exclude', nargs='+', type=int, help='Exclude nodes from calculation')
    parser.add_argument('-i', '--include', dest='include', nargs='+', type=int, help='Include only these nodes in calculation')
    parser.add_argument('-d', '--no_dead', dest='no_dead', action='store_true')
    parser.add_argument('-ex', '--external', dest='external', action='store_true')
    parser.add_argument('-e', '--event', dest='event', action='store_true')
    parser.add_argument('-tx', '--title-x', dest='title_x', action='store', type=str, default='X')
    parser.add_argument('-ty', '--title-y', dest='title_y', action='store', type=str, default='Y')
    parser.add_argument('-dp', '--diff-percentage', dest='diff_p', action='store_true')
    parser.add_argument('-f', '--file', dest='file', help='use the pattern blabla_px_py_babla.yaml')
    parser.add_argument('-n', '--nrg-file', dest='nrg_file', help='use the pattern blabla_px_py_babla.yaml')
    args = parser.parse_args()

    # arr [row][column] - inner = column, outer = row
    pdr_arr = [[[] for x in args.param_x] for y in args.param_y]
    # average path number
    apn_arr = [[[] for x in args.param_x] for y in args.param_y]
    # average network diameter
    and_arr = [[[] for x in args.param_x] for y in args.param_y]

    # ratio of connected nodes
    con_arr = [[[] for x in args.param_x] for y in args.param_y]

    for idx_q, q in enumerate(args.param_x):
        for idx_p, p in enumerate(args.param_y):
            filename = args.file.replace('px', str(q)).replace('py', str(p))
            print('Opening file: ' + filename)
            loader = yaml.safe_load(open(filename, 'r'))

            if args.nrg_file is not None:
                nrg_filename = args.nrg_file.replace('px', str(q)).replace('py', str(p))
                print('Opening file: ' + nrg_filename)
                nrg_loader = yaml.safe_load(open(nrg_filename, 'r'))
            for r_idx, run in enumerate(loader['runs']):
                if 'pdr' in run and 'loc_pdr' in run:
                    if args.nrg_file is not None:
                        pdr_arr[idx_p][idx_q].append(calc_avg_pdr_from_nrg(nrg_loader['runs'][r_idx]))
                    else:
                        pdr_arr[idx_p][idx_q].append(calc_avg_pdr(run))
                    apn_arr[idx_p][idx_q].append(calc_avg_path_num(run))
                    and_arr[idx_p][idx_q].append(calc_avg_nw_diameter(run))
                    con_arr[idx_p][idx_q].append(calc_conn_ratio(run))

    def avg_arr(arr):
        return [[np.average(arr[idx_p][idx_q]) for idx_q, q in enumerate(args.param_x)] for idx_p, p in enumerate(args.param_y)]

    avg_apn_arr = avg_arr(apn_arr)
    avg_and_arr = avg_arr(and_arr)
    avg_pdr_arr = avg_arr(pdr_arr)
    avg_con_arr = avg_arr(con_arr)
    print(con_arr)

    # https://matplotlib.org/stable/gallery/images_contours_and_fields/image_annotated_heatmap.html

    fig, ax = plt.subplots(nrows=4)
    plt.subplots_adjust(wspace=0.1, hspace=0.1)

    for idx, arr in enumerate([avg_pdr_arr, avg_apn_arr, avg_and_arr, avg_con_arr]):
    # Show all ticks and label them with the respective list entries
        im = ax[idx].imshow(arr)
        ax[idx].set_xticks(np.arange(len(args.param_x)), labels=args.param_x)
        ax[idx].set_yticks(np.arange(len(args.param_y)), labels=args.param_y)
        ax[idx].set_xlabel(args.title_x)
        ax[idx].set_ylabel(args.title_y)

    # Rotate the tick labels and set their alignment.
        plt.setp(ax[idx].get_xticklabels(), rotation=45, ha="right",
                 rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
        arr_txt = arr
        if args.diff_p:
            for i in range(len(args.param_y)):
                for j in range(len(args.param_x)):
                    print(type(arr[i][j]))
                    if i != 0 or j != 0:
                        arr_txt[i][j] = "{:.2f}".format(float(arr[i][j]) / float(arr[0][0]) * 100 - 100)+'%'
                    else:
                        arr_txt[i][j] = "{:.2f}".format(float(arr[i][j]))
        for i in range(len(args.param_y)):
            for j in range(len(args.param_x)):
                if args.diff_p:
                    text = ax[idx].text(j, i, arr_txt[i][j],
                                        ha="center", va="center", color="w", fontsize='small')
                else:
                    text = ax[idx].text(j, i, "{:.2f}".format(arr_txt[i][j]),
                                        ha="center", va="center", color="w")
    for idx, label in enumerate(['Average Network PDR', 'Average Path Number', 'Average Network Diameter', 'Average Connected Node Ratio']):
        ax[idx].set_title(label)
    fig.tight_layout()
    plt.show()
