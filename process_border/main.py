#!/bin/env python3

import yaml
import argparse
import pandas as pd


def get_data_from_loader(top):
    if 'runs' in top:
        return top['runs'][0]['loc_pdr']
    else:
        return top

def get_borders(top):
    data=get_data_from_loader(top)
    borders = []
    for i in data:
        for j in i['engines']:
            if j['role'] == 'border' and len(j['hop_pkt_table']) > 0:
                borders.append({'node': i['node'], 'hop_pkt_table': j['hop_pkt_table']})
    return borders


def get_borders_only(top):
    data=get_data_from_loader(top)
    borders = []
    for i in data:
        for j in i['engines']:
            if j['role'] == 'border':
                borders.append(i['node'])
    return borders


def get_rt_num(top):
    data=get_data_from_loader(top)
    rt = []
    for i in data:
        rt_num = 0
        for j in i['engines']:
            if j['role'] == 'external':
                rt_num+= len(j['routing_table'])
        rt.append(rt_num)
    return rt


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
    parser.add_argument('-o', '--out', dest='out', type=str, default='out', help='Output filename')
    args = parser.parse_args()

    means = []
    borders = []
    rt = []
    for filename in args.filename:
        stream = open(filename, 'r')
        loader = yaml.safe_load(stream)
        border_list = get_borders(loader)
        hop_pkt_list = get_hop_pkt_list(border_list)
        table = get_hop_pkt_stat(hop_pkt_list)
        means.append({'hop': table.index, 'mean': table.mean(axis=1)})
        border_num=len(get_borders_only(loader))
        borders.append(border_num)
        rt.append({border_num: get_rt_num(loader)})

    max_hop = max([max(i['hop']) for i in means])
    table = pd.DataFrame(index=list(range(1, max_hop + 1)), columns=range(len(means)))
    for m_idx, m in enumerate(means):
        for idx,i in enumerate(m['hop']):
            table.at[i, m_idx] = m['mean'][i]
    table.fillna(0)

    pd.Series(borders).to_pickle(args.out+'_borders.pickle')
    pd.Series(rt).to_pickle(args.out + '_rt.pickle')
    table.to_pickle(args.out+'_border_pkt.pickle')

    print(pd.read_pickle(args.out+'_borders.pickle'))
