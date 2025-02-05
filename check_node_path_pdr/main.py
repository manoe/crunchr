#!/bin/env python3

import argparse
import logging
logger = logging.getLogger(__name__)
import sys
import yaml

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='check_node_path_pdr', description='Check a node\'s e2e PDR at a specific path',
                                     epilog=':-(')
    parser.add_argument('-n', '--node', dest='node', type=int, help='Node')
    parser.add_argument('-p', '--path', dest='path', type=int, help='Path')
    parser.add_argument('-f', '--file', dest='file', type=str, help='File')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    logger.debug('Filename: ' + str(args.file))
    stream = open(args.file, 'r')
    loader = yaml.safe_load(stream)

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
