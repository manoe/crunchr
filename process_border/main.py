#!/bin/env python3

import yaml
import argparse
import pandas as pd


def get_borders(top):
    if 'runs' in top:
        data = top['runs'][0]['loc_pdr']
    else:
        data = top
    borders = []
    for i in data:
        for j in i['engines']:
            if j['role'] == 'border' and len(j['hop_pkt_table']) > 0:
                borders.append({'node': i['node'], 'hop_pkt_table': j['hop_pkt_table']})
    return borders


def get_hop_pkt_list(borders):
    x_bars = []
    for b_idx, border in enumerate(borders):
        x = [ i['hop'] for i in border['hop_pkt_table']]
        bars = [i['pkt_count'] for i in border['hop_pkt_table']]
        x_bars.append( {'node': border['node'], 'list': dict(zip(x, bars))})
    return x_bars


def get_hop_pkt_stat(x_bars):
    max_hop = max([max(i['list'].keys()) for i in x_bars])
    table = pd.DataFrame(index=list(range(1, max_hop + 1)), columns=list(range(1, len(x_bars) + 1)))

    for b_idx,b in enumerate(x_bars):
        for i in b['list'].keys():
            table.at[i,b_idx] = b['list'][i]
    table.fillna(0)
    return table


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='border_plot', description='Process MSR2MRP border node related stats', epilog=':-(')
    parser.add_argument('filename', help='Input filenames', nargs='*')
    parser.add_argument('-c', '--columns', dest='columns', type=int, default=2, help='Number of columns in plot')
    parser.add_argument('-o', '--out', dest='out', type=str, default='out', help='Output filename')
    args = parser.parse_args()

    means = []
    for filename in args.filename:
        stream = open(filename, 'r')
        loader = yaml.safe_load(stream)
        borders = get_borders(loader)
        hop_pkt_list = get_hop_pkt_list(borders)
        table = get_hop_pkt_stat(hop_pkt_list)
        means.append({'hop': table.index, 'mean': table.mean(axis=1)})
    max_hop = max([max(i['hop']) for i in means])
    table = pd.DataFrame(index=list(range(1, max_hop + 1)), columns=range(len(means)))
    for m_idx, m in enumerate(means):
        for idx,i in enumerate(m['hop']):
            table.at[i, m_idx] = m['mean'][i]
    table.fillna(0)

    table.to_pickle(args.out+'.pickle')


