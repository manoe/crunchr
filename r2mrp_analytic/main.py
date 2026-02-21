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
    res = 1.0 / (1.0 + math.exp(alpha*(dist-args.d0)))
    logger.info('res={}'.format(res))
    return res

def calc_dist(node):
    return math.sqrt(math.pow(node['x'],2)+math.pow(node['y'],2))

def calc_dist_2(node1, node2):
    res = math.sqrt(math.pow(node1['x']-node2['x'],2)+math.pow(node1['y']-node2['y'],2))
    return res


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
    parser.add_argument('-d', '--data', dest='data', choices=['e_p', 'alpha'], help='Data that should be calculated', default='e_p')
    parser.add_argument('-n', '--node-num', dest='node', type=int, help='Number of nodes', default=100)
    parser.add_argument('-x', '--x-num', dest='x', type=int, help='Number of grid points along axis X', default=10)
    parser.add_argument('-y', '--y-num', dest='y', type=int, help='Number of grid points along axis Y', default=10)
    parser.add_argument('-l', '--log-level', dest='log_level', choices=['debug','info','none'], default='none', help='Log level')
    parser.add_argument('-gd','--grid-distance', dest='grid_distance', type=float, help='Grid cell distance in meters', default=20)
    parser.add_argument('-q', '--qos', dest='qos', type=float, help='QoS filter value', default=0.8)
    parser.add_argument('-nt', '--num-test', dest='nt', type=int, help='Number of link test messages', default=10)
    parser.add_argument('-rd', '--ref_dist', dest='d0', type=float, help='Reference distance', default=1)
    parser.add_argument('-a', '--alpha', dest='alpha', type=float, help='Attenuation coefficient', default=2.5)
    parser.add_argument('-i', '--iter', dest='iter', type=int, help='Number of iterations, if alpha is calculated', default=100)

    args = parser.parse_args()

    alpha = 2.5


    match args.log_level:
        case 'debug':
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        case 'info':
            logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    if args.x * args.y < args.node:
        logging.error('Number of grid points lower than number of nodes')

    logger.info('Constructing node array')
    nodes = []
    for i in range(args.x):
        for j in range(args.y):
            if i * args.x + j < args.node:
                nodes.append({'num': i * args.x + j, 'x': i * args.grid_distance, 'y': j * args.grid_distance, })

    match args.data:
        case 'e_p':
            print('Calculating E[P], expected number of paths:')
            logger.info('Node array done, size:{}'.format(len(nodes))+' on a field of {}'.format(args.x)+'x{}'.format(args.y))
            print('E[P]={}'.format(calc_e_p(nodes)))
        case 'alpha':
            print('Calculating alpha values:')
            print('Setting initial alpha values for each node')
            for i,n in enumerate(nodes):
                if i == 0:
                    continue
                nodes[i]['alpha'] = { j: 0.0 for j in range(1,args.node) }
                nodes[i]['alpha'][n['num']]=calc_q_us(calc_dist(n))

            print('Starting iteration')
            for it in range(args.iter):
                print('Iteration step {}.'.format(it))
                for i,n in enumerate(nodes):
                    if i == 0:
                        continue
                    for k in n['alpha'].keys():
                        nodes[i]['alpha'][k] = n['alpha'][k] + (1 - n['alpha'][k]) * (1 - math.prod([ u['alpha'][k]/math.fsum(u['alpha'].values()) * calc_q_us(calc_dist_2(n,u)) if math.fsum(u['alpha'].values()) > 0 else 0 for u in nodes[1:i] + nodes[i + 1:]]))

