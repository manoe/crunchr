#!/bin/env python3

import logging
logger = logging.getLogger(__name__)
import yaml
import argparse
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='pick_border', description='Pick a border node', epilog=':-(')
    parser.add_argument('filename', help='Probably loc_pdr.yaml')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    stream = open(args.filename, 'r')
    loader = yaml.safe_load(stream)

    borders = [ i for i in loader if 'border' in [j['role'] for j in i['engines'] ] ]

    b_d = [ {'node': i['node'], 'pkt': i['engines'][0]['routing_table'][0]['pkt_count']}  for i in borders ]

    b_d = sorted(b_d, key=lambda d: d['pkt'])
    print(b_d[-1]['node'])
    logger.debug('Sorted array: ' + str(b_d))
    logger.debug('Candidate: ' + str(b_d[-1]))
