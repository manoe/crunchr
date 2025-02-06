#!/bin/env python3

import argparse
import logging
logger = logging.getLogger(__name__)
import sys
import yaml
import networkx as nx
import copy

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
                                # ulgy hack
                                nw.add_edge(node['node'], re['node'], pathid=[0], secl=re['secl'],
                                            engine=engine['engine'])
                        else:
                            nw.add_edge(node['node'], re['node'], pathid=[], secl=re['secl'], engine=engine['engine'])
                roles.append((engine['engine'], engine['role']))
            nx.set_node_attributes(nw, {node['node']: roles}, 'roles')
    return nw

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='check_node_path_pdr', description='Check a node\'s e2e PDR at a specific path',
                                     epilog=':-(')
    parser.add_argument('-n', '--node', dest='node', type=int, help='Node')
    parser.add_argument('-p', '--path', dest='path', type=int, help='Path', nargs='?')
    parser.add_argument('-f', '--file', dest='file', type=str, help='File')
    parser.add_argument('-c', '--config', dest='config', action='store_true', help='Generate config')
    parser.add_argument('-q', '--query', dest='query', action='store_true', help='Query')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    logger.debug('Filename: ' + str(args.file))
    stream = open(args.file, 'r')
    loader = yaml.safe_load(stream)

    if args.query:
        paths = [l['pathid'] for i in loader if i['node'] == args.node for j in i['engines'] for k in j['routing_table'] for l in k['pathid'] ]
        nw = construct_graph(loader)

        for p in paths:
            t_nw = copy.deepcopy(nw)
            for i in nw.edges(data=True):
                if p not in i[2]['pathid']:
                    t_nw.remove_edge(i[0], i[1])
            spath = list(nx.all_simple_edge_paths(t_nw, args.node,p))

            if len(spath) > 1:
                logger.error('Several paths available')
                exit(1)
            nodes = [i[1] for i in spath[0]]
            if not args.config:
                print('from '+str(args.node)+' via pathid '+str(p)+' node are '+str(nodes))
            else:
                for idx,node in enumerate(nodes):
                    print(str(p)+' '+str(idx+1)+' '+str(node))
        exit(0)

    if not args.path:
        logger.error('No path specified')
        exit(1)

    sink_engines = [ j for i in loader for j in i['engines'] if j['role'] == 'central']

    recv_pkt = 0

    for sink_engine in sink_engines:
        logger.debug('Engine: ' + str(sink_engine['engine']))
        for te in sink_engine['traffic_table']:
            logger.debug('TE node: ' + str(te['node']))
            if te['node'] == args.node:
                for pe in te['pathid']:
                    logger.debug('PE: ' + str(pe['pathid']))
                    logger.debug('PE pkt: ' + str(pe['pkt']))
                    if pe['pathid'] == args.path:
                        recv_pkt = pe['pkt']

    sent_pkt = 0
    for i in loader:
        if i['node'] == args.node:
            for j in i['engines']:
                if 'routing_table' in j:
                    for k in j['routing_table']:
                        for l in k['pathid']:
                            if l['pathid'] == args.path:
                                sent_pkt = k['orig_pkt_count']

    if sent_pkt > 0:
        print('Node: '+str(args.node))
        print('Path: '+str(args.path))
        print('Sent packet: '+str(sent_pkt))
        print('Received packet: '+str(recv_pkt))
        print('PDR: '+str(float(recv_pkt)/float(sent_pkt)))
