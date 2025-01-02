#!/bin/env python3

import argparse
import logging
logger = logging.getLogger(__name__)
import pandas as pd
import sys
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import networkx as nx
import yaml

from matplotlib import rcParams
rcParams['font.family'] = ['serif']
rcParams['font.serif'] = ['Times New Roman']

def construct_graph(run):
    nw = nx.MultiDiGraph()
    for node in run:
        nw.add_node(node['node'], master=node['master'], pos=[node['x'], node['y']])
        if 'engines' in node:
            roles = []
            for engine in node['engines']:
                if 'routing_table' in engine:
                    for re in engine['routing_table']:
                        pathid = [pe['pathid'] for pe in re['pathid']]
                        if engine['role'] == 'external':
                            secl = False
                            for k in re['pathid']:
                                if k['secl']:
                                    secl = True
                            nw.add_edge(node['node'], re['node'], pathid=pathid, secl=secl, engine=engine['engine'])
                        elif engine['role'] == 'border':
                            if re['node'] in pathid:
                                nw.add_edge(node['node'], re['node'], pathid=pathid, engine=engine['engine'])
                            else:
                                nw.add_edge(node['node'], re['node'], secl=re['secl'], engine=engine['engine'])
                        else:
                            nw.add_edge(node['node'], re['node'], secl=re['secl'], engine=engine['engine'])
                roles.append((engine['engine'], engine['role']))
            nx.set_node_attributes(nw, {node['node']: roles}, 'roles')
    return nw


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='msr2mrp_meas_1_plot', description='Process MSR2MRP border node related stats', epilog=':-(')
    parser.add_argument('filename', help='Input filename template, use $1 for params, $2 for data types as wildcard')
    parser.add_argument('-p', '--parameters', dest='params', nargs='+', help='Parameter space')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    parser.add_argument('-pl', '--plot', dest='plot', choices=['network', 'bar','hist'], help='Plot type')
    parser.add_argument('-pd', '--plot-data', dest='plot_data', choices=['disjoint', 'pathnum'], default='disjoint', help='Plot data')
    parser.add_argument('-n', '--network', dest='network', type=str, nargs='*', help='Number of nodes')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    if args.plot == 'network' and len(args.params) != len(args.network):
        logger.error('Number of parameters and number of networks must match')
        exit(1)

    record = []


    for param in args.params:
        filename = args.filename.replace('$1', param)
        logger.debug('Base filename: ' + str(filename))

        dmp = pd.read_pickle(filename.replace('$2', 'dmp'))
        rm = pd.read_pickle(filename.replace('$2', 'rm'))
        sink = pd.read_pickle(filename.replace('$2', 'sink'))
        iso  = pd.read_pickle(filename.replace('$2', 'sink'))
        record.append({'filename': filename, 'dmp':dmp, 'rm':rm, 'sink':sink, 'iso':iso})

    match args.plot:
        case 'bar':
            fig, axs = plt.subplots(nrows=4, ncols=1)
            sink_num = [ np.average(r['sink'].mean(axis=1)) for r in record ]
            sink_err = [ np.average(r['sink'].std(axis=1)) for r in record ]
            axs[0].set_title('Sink')
            bars = axs[0].bar(args.params, sink_num)
            axs[0].bar_label(bars, label_type='edge')
            axs[0].errorbar(args.params, sink_num, sink_err, fmt='.', color='Black', elinewidth=2, capthick=10, errorevery=1, alpha=0.5, ms=4, capsize=2)

            path_num = [ np.average(r['rm'].mean(axis=1)) for r in record ]
            path_err = [ np.average(r['rm'].std(axis=1)) for r in record ]
            axs[1].set_title('Path')
            bars = axs[1].bar(args.params, path_num)
            axs[1].bar_label(bars, label_type='edge')
            axs[1].errorbar(args.params, path_num, path_err, fmt='.', color='Black', elinewidth=2, capthick=10, errorevery=1, alpha=0.5, ms=4, capsize=2)

            dmp_num = [np.average(r['dmp'].mean(axis=1)) for r in record]
            dmp_err = [np.average(r['dmp'].std(axis=1)) for r in record]

            axs[2].set_title('Disjointness')
            bars = axs[2].bar(args.params, dmp_num)
            axs[2].bar_label(bars, label_type='edge')
            axs[2].errorbar(args.params, dmp_num, dmp_err, fmt='.', color='Black', elinewidth=2, capthick=10, errorevery=1, alpha=0.5, ms=4,
                         capsize=2)

            two_disj_num = [ (r['dmp'] ==0).sum(axis=1).div(r['dmp'].notna().sum(axis=1)).mean() for r in record ]
            two_disj_err =[ (r['dmp'] ==0).sum(axis=1).div(r['dmp'].notna().sum(axis=1)).std() for r in record ]

            axs[3].set_title('Two disj probability')
            bars = axs[3].bar(args.params, two_disj_num)
            axs[3].errorbar(args.params, two_disj_num, two_disj_err, fmt='.', color='Black', elinewidth=2, capthick=10, errorevery=1, alpha=0.5, ms=4,
                         capsize=2)
            axs[3].bar_label(bars, label_type='edge')
            plt.tight_layout()
            plt.show()
        case 'network':
            fig, axs = plt.subplots(nrows=int(np.ceil(len(record[1:]) / 2)), ncols=2)
            axs_arr = axs.ravel()

            for idx_r,r in enumerate(record[1:]):
                stream = open(args.network[idx_r+1], 'r')
                loader = yaml.safe_load(stream)
                nw = construct_graph(loader)
                if args.plot_data == 'disjoint':
                    color = [r['dmp'].mean(axis=0)[i] if i in r['dmp'].mean(axis=0).index else 0 for i in nw.nodes()]
                else:
                    color = [r['rm'].mean(axis=0)[i] if i in r['rm'].mean(axis=0).index else 0 for i in nw.nodes()]

                pos = nx.get_node_attributes(nw, 'pos')

                nx.draw_networkx_nodes(nw, ax=axs_arr[idx_r], pos=pos, node_color=color, cmap='viridis', node_size=200)
                nx.draw_networkx_edges(nw, ax=axs_arr[idx_r], pos=pos)

                cmap = cm.ScalarMappable(cmap='viridis')
                cmap.set_clim(vmin=np.min(color), vmax=np.max(color))
                fig.colorbar(cmap, ax=axs_arr[idx_r], orientation='vertical', label='Some Units')
        case 'hist':
            fig, axs = plt.subplots(nrows=int(np.ceil(len(record[1:]) / 2)), ncols=2)
            axs_arr = axs.ravel()

            for idx_r, r in enumerate(record[1:]):
                if args.plot_data == 'disjoint':
                    data_src = [i for i in r['dmp'].values.ravel() if not np.isnan(i)]
                    bins = np.arange(0,1.1,0.1)
                else:
                    data_src = [i for i in r['rm'].values.ravel() if not np.isnan(i)]
                    bins = 'auto'
                counts, bins = np.histogram(data_src, bins=bins)
                axs_arr[idx_r].stairs(counts, bins)
        case _:
            logger.error('Plot param unknown')
            exit(1)

    plt.tight_layout()
    plt.show()

