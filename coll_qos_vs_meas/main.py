#!/bin/env python3

import yaml
import argparse
import logging
logger = logging.getLogger(__name__)
import sys
import pandas as pd

def get_rreq_entry(engine, node):
    for rq in engine['rreq_table']:
        if rq['node'] == node:
            return rq
    logger.debug('Entry '+str(engine['rreq_table'])+'does not contain '+str(node))
    raise Exception("RREQ entry does not exists")


def get_pkt_entry(pkt_table, node):
    for p in pkt_table:
        if p['node'] == node:
            return p
    raise Exception("PKT entry does not exists")


def coll_nodes_and_meas(node):
    ret_val = []
    for e in node['engines']:
        if 'routing_table' in e:
            for rt in e['routing_table']:
                rq = get_rreq_entry(e, rt['node'])
                p = get_pkt_entry(node['pkt_table'], rt['node'])
                ret_val.append({'path':(node['node'],rt['node']), 'meas_q': float(rq['ack_count'])/float(rq['pkt_count']), 'meas_t': p['ack_count']/p['pkt_count']})
    return ret_val

def get_data_from_loader(top):
    if 'runs' in top:
        return top['runs'][0]['loc_pdr']
    else:
        return top


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='coll_qos_vs_meas', description='Collect achieved versus measured PDR value', epilog=':-(')
    parser.add_argument('filenames', help='Input filenames', nargs='*')
    parser.add_argument('-o', '--out', dest='out', type=str, default='out', help='Output filename')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    args = parser.parse_args()

    results = []

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    for f_idx, filename in enumerate(args.filenames):
        stream = open(filename, 'r')
        print(str(filename)+' '+str(f_idx+1)+'/'+str(len(args.filenames)))
        loader = yaml.safe_load(stream)
        data = get_data_from_loader(loader)
        res = [ coll_nodes_and_meas(n) for n in data]
        for r in res:
            if len(r) > 0:
                results+=r

    pd.Series(results).to_pickle(args.out+'.pickle')