#!/bin/env python3

import argparse
import logging
import matplotlib

logger = logging.getLogger(__name__)
import pandas as pd
import sys
import matplotlib.pyplot as plt
from matplotlib import colormaps
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
    parser.add_argument('-pd', '--plot-data', dest='plot_data', choices=['disjoint', 'pathnum', 'border', 'sinkpath', 't-pdr'], default='disjoint', help='Plot data')
    parser.add_argument('-n', '--network', dest='network', type=str, nargs='*', help='Network plot files')
    parser.add_argument('-o', '--outlier', dest='outlier', type=float,  help='Outlier threshold', default=0.0)
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

        dmp   = pd.read_pickle(filename.replace('$2', 'dmp'))
        rm    = pd.read_pickle(filename.replace('$2', 'rm'))
        sink  = pd.read_pickle(filename.replace('$2', 'sink'))
        iso   = pd.read_pickle(filename.replace('$2', 'sink'))
        role  = pd.read_pickle(filename.replace('$2', 'role'))
        min_d = pd.read_pickle(filename.replace('$2', 'min_d'))
        t_pdr = pd.read_pickle(filename.replace('$2', 't_pdr'))
        record.append({'filename': filename, 'dmp':dmp, 'rm':rm, 'sink':sink, 'iso':iso, 'role':role, 'min_d':min_d, 't_pdr': t_pdr})

    match args.plot:
        case 'bar':
            match args.plot_data:
                case 'sinkpath':
                    x = -0.07
                    fig, axs = plt.subplots(nrows=2, ncols=1, layout='compressed')
                    sink_num = [np.average(r['sink'].mean(axis=1)) for r in record]
                    sink_err = [np.average(r['sink'].std(axis=1)) for r in record]
                    axs[0].set_title('(a)', loc='left', pad=15, x=x)
                    bars = axs[0].bar(args.params, sink_num)
                    axs[0].set_ylabel('Average reachable sinks')
                    axs[0].set_xlabel('Available sinks')
                    axs[0].set_ylim([0, 6])
                    axs[0].bar_label(bars, label_type='center',fmt='{0:.4f}')
                    axs[0].errorbar(args.params, sink_num, sink_err, fmt='.', color='Black', elinewidth=2, capthick=1,
                                    errorevery=1, alpha=0.5, ms=4, capsize=5)

                    path_num = [np.average(r['rm'].mean(axis=1)) for r in record]
                    path_err = [np.average(r['rm'].std(axis=1)) for r in record]
                    axs[1].set_title('(b)', loc='left', pad=15, x=x)
                    axs[1].set_ylabel('Average path number')
                    axs[1].set_xlabel('Available sinks')
                    bars = axs[1].bar(args.params, path_num)
                    axs[1].bar_label(bars, label_type='center', fmt='{0:.2f}', padding=0)
                    axs[1].set_ylim([0, 9])
                    axs[1].errorbar(args.params, path_num, path_err, fmt='.', color='Black', elinewidth=2, capthick=1,
                                    errorevery=1, alpha=0.5, ms=4, capsize=5)
                case 'disjoint':
                    x = -0.08

                    fig, axs = plt.subplots(nrows=2, ncols=1, layout='compressed')

                    dmp_num = [np.average(r['dmp'].mean(axis=1)) for r in record]
                    dmp_err = [np.average(r['dmp'].std(axis=1)) for r in record]

                    axs[0].set_title('(a)', loc='left', pad=15, x=x)
                    bars = axs[0].bar(args.params, dmp_num)
                    axs[0].bar_label(bars, label_type='center', fmt='{0:.2f}')
                    axs[0].errorbar(args.params, dmp_num, dmp_err, fmt='.', color='Black', elinewidth=2, capthick=1,
                                    errorevery=1, alpha=0.5, ms=4,
                                    capsize=5)
                    axs[0].set_ylabel('d-score')
                    axs[0].set_xlabel('Available sinks')
                    axs[1].set_xlabel('Available sinks')

                    ind = np.arange(len(record))
                    axs[1].set_title('(b)', loc='left', pad=15, x=x)
                    axs[1].set_ylabel('N-disjointness probability')
                    width = 0.2
                    bars = []
                    for idx_p, p in enumerate(np.arange(1,5)):
                        disj_num = [(r['min_d'] > p).sum(axis=1).div(r['min_d'].notna().sum(axis=1)).mean() for r in record]
                        disj_err = [(r['min_d'] > p).sum(axis=1).div(r['min_d'].notna().sum(axis=1)).std() for r in record]
                        bars.append(axs[1].bar(ind+width*idx_p, disj_num, width=width))
                        axs[1].bar_label(bars[-1], label_type='center', fmt='{0:.2f}')
                        axs[1].errorbar(ind+width*idx_p, disj_num, disj_err, fmt='.', color='Black', elinewidth=2, capthick=1,
                                    errorevery=1, alpha=0.5, ms=4,
                                    capsize=5)

                    plt.xticks(ind + width*1.5, args.params)
                    plt.legend(tuple(bars), tuple(np.arange(2,6)), title='Minimum disjointness', loc='center',
                                ncol=5, bbox_to_anchor=(0.5, -0.6))
                    # https://stackoverflow.com/questions/44071525/matplotlib-add-titles-to-the-legend-rows/44072076#44072076
                case _:
                    logger.error('Unknown plot type for bar: ' + args.plot_data)
                    exit(1)

        case 'network':
            figsize = rcParams["figure.figsize"]
            figsize = [i*2 for i in figsize]
            figsize[0] = figsize[0]*0.85
            fig, axs = plt.subplots(nrows=int(np.ceil(len(record) / 2)), ncols=2, layout='compressed', figsize=figsize)
            axs_arr = axs.ravel()

            vmin=[]
            vmax=[]
            title = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)']
            x=0.04
            for idx_r,r in enumerate(record):
                stream = open(args.network[idx_r], 'r')
                loader = yaml.safe_load(stream)
                nw = construct_graph(loader)
                alpha=1
                match args.plot_data:
                    case 'disjoint':
                        clabel='d-score'
                        color = [r['dmp'].mean(axis=0)[i] if i in r['dmp'].mean(axis=0).index and r['dmp'][i].notna().sum()/len(r['dmp'][i]) > args.outlier else 0 for i in nw.nodes()]
                        vmin.append(0)
                        vmax.append(1)
                    case 'pathnum':
                        color = [r['rm'].mean(axis=0)[i] if i in r['rm'].mean(axis=0).index and
                                                    r['dmp'][i].notna().sum() / len(r['dmp'][i]) > args.outlier else 0 for i in nw.nodes()]
                        vmin.append(min(color))
                        vmax.append(max(color))
                        clabel='Path number'
                    case 'border':
                        color = [r['role'][i].value_counts()['border']/r['role'][i].value_counts().sum() if 'border' in r['role'][i].value_counts() else 0 for i in nw.nodes()]
                        #alpha = [ 1 if i > 0 else 0 for i in color]
                        edgecolors = [  '#1f78b4ff' for i in color]
                        vmin.append(min(color))
                        vmax.append(max(color))
                        clabel='Border role probability'
                    case _:
                        'none'
                edgecolors = ['#1f78b4ff' for i in color]
                pos = nx.get_node_attributes(nw, 'pos')
                node_colors=colormaps['viridis']([i/max(vmax) for i in color])
                if args.plot_data == 'border':
                    node_colors = [ i if color[idx] != 0 else [1, 1, 1, 1.      ] for idx, i in enumerate(node_colors)]
                nx.draw_networkx_nodes(nw, ax=axs_arr[idx_r], pos=pos, node_color=node_colors, node_size=200, alpha=alpha, edgecolors=edgecolors)
                nx.draw_networkx_edges(nw, ax=axs_arr[idx_r], pos=pos)
                axs_arr[idx_r].axis('off')
                axs_arr[idx_r].set_title(title[idx_r], loc='left', pad=5, x=x)
            cmap = cm.ScalarMappable(cmap='viridis')
            cmap.set_clim(vmin=min(vmin), vmax=max(vmax))

                #fig.subplots_adjust(right=0.8)
                #cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
            cax, kw = matplotlib.colorbar.make_axes([ax for ax in axs.flat],aspect=40)
            plt.colorbar(cmap, cax=cax, **kw, label=clabel)
        case 'hist':
            #fig, axs = plt.subplots(nrows=int(np.ceil(len(record[1:]) / 2)), ncols=2)
            fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(rcParams["figure.figsize"][0], rcParams["figure.figsize"][1]*0.75))
            x=-0.23
            axs.set_ylabel('Probability')
            for idx_r, r in enumerate(record):
                match  args.plot_data:
                    case 'disjoint':
                        data_src = [i for i in r['dmp'].values.ravel() if not np.isnan(i)]
                        orig_bins = np.arange(0,1.1,0.1)
                        axs.set_xlabel('d-score')
                        counts, bins = np.histogram(data_src, bins=orig_bins)
                        axs.stairs(counts / sum(counts), bins + 0.002 * (idx_r - 1))
                    case 'pathnum':
                        data_src = [i for i in r['rm'].values.ravel() if not np.isnan(i)]
                        orig_bins = np.arange(0, max(r['rm'].values.ravel())+1)
                        axs.set_xticks(orig_bins)
                        axs.set_xticklabels(["{0:.0f}".format(x) for x in orig_bins])
                        axs.set_xlabel('Path number')
                        #bins = 'auto'
                        counts, bins = np.histogram(data_src, bins=orig_bins)
                        axs.stairs(counts / sum(counts), bins + 0.01 * (idx_r - 1))
                    case 't-pdr':
                        data_src = [i for i in r['t_pdr'].values.ravel() if not np.isnan(i)]
                        orig_bins = np.arange(0, 1.1, 0.1)
                        axs.set_xlabel('End-to-end PDR')
                        counts, bins = np.histogram(data_src, bins=orig_bins)
                        axs.stairs(counts / sum(counts), bins + 0.002 * (idx_r - 1))
                    case _:
                        logger.error('Unknown plot type for histogram: ' + args.plot_data)
                        exit(1)
                axs.legend(labels=args.params, title='Sink amount', ncol=5, loc='upper left')
                axs.set_ylim([0, 1.01])


        case _:
            logger.error('Plot param unknown')
            exit(1)

    if args.plot != 'network' and args.plot != 'bar':
        plt.tight_layout()
    plt.show()
    fig.savefig(str(args.plot)+'_'+str(args.plot_data)+".pdf", bbox_inches='tight')

