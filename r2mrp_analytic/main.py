#!/bin/env python3
from secrets import choice

import numpy as np
import matplotlib.pyplot as plt
import argparse
from dataclasses import dataclass
import math
import logging
logger = logging.getLogger(__name__)
import sys

def calc_pd(dist):
    logger.info('dist={}'.format(dist))
    lres = math.log(args.rd/dist, 10)
    if lres < -1:
        res = 0
    else:
        res = 1 + lres
    logger.info('res={}'.format(res))
    return res

def calc_dist(node):
    return math.sqrt(math.pow(node['x'],2)+math.pow(node['y'],2))

def calc_q_us(dist):
    # \sum_{k=ceil(n * tau)}{n}
    res = 0.0
    for k in range(math.ceil(args.qos * args.nt),args.nt+1):
        logger.info('k={}'.format(k))
        res += math.comb(args.nt,k) * pow(calc_pd(dist),k) * pow(1 - calc_pd(dist),args.nt-k)
    return res

def calc_e_p(nodes):
    res = 0.0
    for node in nodes[1:]:
        res += calc_q_us(calc_dist(node))
    return res

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='r2mrp_analytic', description='Calculate R2MRP-specific data analytically', epilog=':-(')
    parser.add_argument('-d', '--data', dest='data', choices=['e_p'], help='Data that should be calculated', default='e_p')
    parser.add_argument('-n', '--node-num', dest='node', type=int, help='Number of nodes', default=100)
    parser.add_argument('-x', '--x-num', dest='x', type=int, help='Number of grid points along axis X', default=10)
    parser.add_argument('-y', '--y-num', dest='y', type=int, help='Number of grid points along axis Y', default=10)
    parser.add_argument('-l', '--log-level', dest='log_level', choices=['debug','info','none'], default='none', help='Log level')
    parser.add_argument('-gd','--grid-distance', dest='grid_distance', type=float, help='Grid cell distance in meters', default=20)
    parser.add_argument('-q', '--qos', dest='qos', type=float, help='QoS filter value', default=0.8)
    parser.add_argument('-nt', '--num-test', dest='nt', type=int, help='Number of link test messages', default=10)
    parser.add_argument('-rd', '--ref_dist', dest='rd', type=float, help='Reference distance', default=10)

    args = parser.parse_args()

    match args.log_level:
        case 'debug':
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        case 'info':
            logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    if args.x * args.y < args.node:
        logging.error('Number of grid points lower than number of nodes')

    match args.data:
        case 'e_p':
            print('Calculating E[P], expected number of paths:')
            logger.info('Constructing node array')
            nodes = []
            for i in range(args.x):
                for j in range(args.y):
                    if i*args.x+j < args.node:
                        nodes.append( {'num': i*args.x+j, 'x': i*args.grid_distance, 'y': j*args.grid_distance} )

            logger.info('Node array done, size:{}'.format(len(nodes))+' on a field of {}'.format(args.x)+'x{}'.format(args.y))
            print('E[P]={}'.format(calc_e_p(nodes)))


