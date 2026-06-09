#!/bin/env python3
from copy import deepcopy
from secrets import choice

import numpy as np
import matplotlib.pyplot as plt
import argparse
from dataclasses import dataclass
import math
import logging
logger = logging.getLogger(__name__)
import sys
import copy
from collections import deque

def calc_pd_log(dist):
    logger.debug('dist={}'.format(dist))
    res = 1.0 / (1.0 + math.exp(alpha*(dist-args.d0)))
    logger.debug('res={}'.format(res))
    return res

def calc_pd_div(dist):
    logger.info('dist={}'.format(dist))
    lres = math.log(args.d0/dist, 10)
    if lres < -1:
        res = 0
    else:
        res = 1 + lres
    logger.info('res={}'.format(res))
    return res

def calc_dist(node):
    return math.sqrt(math.pow(node['x'],2)+math.pow(node['y'],2))

def calc_dist_2(node1, node2):
    res = math.sqrt(math.pow(node1['x']-node2['x'],2)+math.pow(node1['y']-node2['y'],2))
    return res

def calc_q(dist):
    res = 0.0
    for k in range(math.ceil(args.qos * args.nt),args.nt+1):
        logger.debug('k={}'.format(k))
        res += math.comb(args.nt,k) * pow(calc_pd(dist),k) * pow(1 - calc_pd(dist),args.nt-k)
    logger.info('q={}'.format(res))
    return res

def calc_b(dist):
    return calc_q(dist) * calc_pd(dist)

def calc_q_us(dist):
    # \sum_{k=ceil(n * tau)}{n}
    res = 0.0
    for k in range(math.ceil(args.qos * args.nt),args.nt+1):
        logger.debug('k={}'.format(k))
        res += math.comb(args.nt,k) * pow(calc_pd(dist),k) * pow(1 - calc_pd(dist),args.nt-k)
    logger.info('q_us={}'.format(res))
    return calc_pd(dist) * res

def calc_e_p(nodes):
    res = 0.0
    for node in nodes[1:]:
        res += calc_q_us(calc_dist(node))
    return res

def peer_arr(nodes, node):
    res = []
    for n in nodes:
        if calc_dist_2(n, node) < args.pr and n['num'] != node['num']:
            res.append(n)
    return res

def calc_beta(alpha_n, alpha_n_1):
    delta = alpha_n-alpha_n_1
    beta = np.ndarray(shape=alpha_n.shape)
    for v in range(1,args.node):
        m_v=delta[v,:].sum()
        for p in range(1,args.node):
            beta[v,p]=delta[v,p]/(m_v+args.epsilon)
    return beta

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='r2mrp_analytic', description='Calculate R2MRP-specific data analytically', epilog=':-(')
    parser.add_argument('-d', '--data', dest='data', choices=['e_p', 'alpha'], help='Data that should be calculated', default='alpha')
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
    parser.add_argument('-e', '--epsilon', dest='epsilon', type=float, help='Epsilon',
                        default=0.00001)
    parser.add_argument('-r', '--radio', dest='radio', choices=['log', 'div'], help='Radio channel',
                        default='log')
    parser.add_argument('-m', '--method', dest='method', choices=['old','new'], default='new',
                        help='Log level')
    parser.add_argument('-pr', '--peer-radius', dest='pr', type=float, default=40,
                        help='Distance of peers')

    args = parser.parse_args()

    alpha = 2.5


    match args.log_level:
        case 'debug':
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        case 'info':
            logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        case 'none':
            logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

    if args.x * args.y < args.node:
        logging.error('Number of grid points lower than number of nodes')
        exit(1)

    if args.radio == 'log':
        calc_pd = calc_pd_log
    else:
        calc_pd = calc_pd_div

    logger.info('Constructing node array')
    nodes = {}
    for i in range(args.x):
        for j in range(args.y):
            if i * args.x + j < args.node:
                nodes[i * args.x + j]={ 'x': i * args.grid_distance, 'y': j * args.grid_distance}

    match args.data:
        case 'e_p':
            print('Calculating E[P], expected number of paths:')
            logger.info('Node array done, size:{}'.format(len(nodes))+' on a field of {}'.format(args.x)+'x{}'.format(args.y))
            print('E[P]={}'.format(calc_e_p(nodes)))
        case 'alpha':
            print('Calculating alpha values')
            print('Setting initial alpha values for each node')

            alpha_queue = deque()
            alpha_queue.appendleft( np.zeros(shape=(args.node, args.node)))

            first = np.zeros(shape=(args.node, args.node))
            for i in range(1, args.node):
                first[i,i] = calc_b(calc_dist(nodes[i]))
            a_queue = deque()
            o_queue = deque()


            a_queue.appendleft(np.zeros(shape=(args.node)))
            o_queue.appendleft(np.zeros(shape=(args.node)))

            a_queue.appendleft(np.array([ calc_pd(calc_dist(nodes[n])) if n != 0 else 0 for n in range(0,args.node) ]) )
            o_queue.appendleft(copy.deepcopy(a_queue[0]))

            alpha_queue.appendleft(first)
            beta = copy.deepcopy(first)

            for i in range(2, args.iter):

                alpha = np.zeros(shape=(args.node, args.node))

                a_arr = [0.0]
                o_arr = [0.0]
                for v in range(1, args.node):
                    if i == 1:
                        a = calc_pd(calc_dist(nodes[v]))
                        o = calc_pd(calc_dist(nodes[v]))
                        a_arr.append(a)
                        o_arr.append(o)

                    else:
                        a_prod_body = [ 1 - math.fsum(beta[u,:]) * calc_pd(calc_dist_2( nodes[u],nodes[v] )) for u in range(1,args.node) if u != v ]
                        a = 1 - math.prod(a_prod_body)
                        a_arr.append(a)
                        o = 1 - math.fsum([ o_elem[v] for o_elem in o_queue]) * a
                        o_arr.append(o)

                    for p in range(1, args.node):
                        prod_body = [ 1 - beta[u,p] * calc_b(calc_dist_2( nodes[u],nodes[v] )) for u in range(1, args.node) if u != v ]
                        alpha[v, p] = alpha_queue[1][v,p] + o * (1 - alpha_queue[1][v,p]) * (1 - math.prod(prod_body) )
                alpha_queue.appendleft(alpha)
                o_queue.appendleft(o_arr)
                a_queue.appendleft(a_arr) # felesleges
                beta = calc_beta(alpha_queue[0],alpha_queue[1])

#
#            for i,n in enumerate(nodes):
#                if i == 0:
#                    continue
#                nodes[i]['alpha'] = { j: 0.0 for j in range(1,args.node) }
#            nodes_n_2 = copy.deepcopy(nodes)
#
#            for i, n in enumerate(nodes):
#                if i == 0:
#                    continue
#                nodes[i]['alpha'][n['num']]=calc_q_us(calc_dist(n))
#            nodes_n_1 = copy.deepcopy(nodes)
#
#
#            print('Starting iteration')
#            for it in range(args.iter):
#                print('Iteration step {}.'.format(it))
#                for i,n in enumerate(nodes_n_1):
#                    if i == 0:
#                        continue
#                    for k in n['alpha'].keys():
#                        if k == n['num']:
#                            continue
#                        if args.method == 'old':
#                            nodes[i]['alpha'][k] = n['alpha'][k] + (1 - n['alpha'][k]) * (1 - math.prod([1 - u['alpha'][k] / math.fsum(u['alpha'].values()) * calc_q_us(calc_dist_2(n, u))
#                                            if math.fsum(u['alpha'].values()) > 0  else 1 for u in peer_arr(nodes_n_1[1:], n)]))
#                        else:
#                            nodes[i]['alpha'][k] = n['alpha'][k] + (1 - n['alpha'][k]) * (1 - math.prod([ 1 - (u['alpha'][k] - u_1['alpha'][k] )/(math.fsum(u['alpha'].values())-math.fsum(u_1['alpha'].values()) + args.epsilon) * calc_q_us(calc_dist_2(n,u))
#                                                                                                      #if math.fsum(u['alpha'].values())-math.fsum(u_1['alpha'].values()) > 0 and u['adv'] else 1
#                                                                                                      for u, u_1 in zip(peer_arr(nodes_n_1[1:],n), peer_arr(nodes_n_2[1:],n))]))
#                for i,n in enumerate(nodes[1:]):
#                    for j in n['alpha']:
#                        if n['alpha'][j] > 0:
#                            nodes[i]['adv'] = False
#                nodes_n_2 = copy.deepcopy(nodes_n_1)
#                #print(str(nodes[1]['alpha'][1])+' '+str(nodes[1]['alpha'][1]-nodes_n_1[1]['alpha'][1]))
#                nodes_n_1 = copy.deepcopy(nodes)
#                if it%10 == 0:
#                    n_alpha = []
#                    n_1_alpha = []
#                    for i, j in zip(nodes_n_1[1:], nodes_n_2[1:]):
#                        n_alpha += list(i['alpha'].values())
#                        n_1_alpha += list(j['alpha'].values())
#
#                    alpha_diff = np.subtract(n_alpha, n_1_alpha)
#
#                    print('diff L2 norm at '+str(it)+': ' + str(math.sqrt(np.sum(np.power(alpha_diff, 2)))))
#            n_alpha = []
#            n_1_alpha = []
#            for i,j in zip(nodes_n_1[1:], nodes_n_2[1:]):
#                n_alpha += list(i['alpha'].values())
#                n_1_alpha += list(j['alpha'].values())
#
#            alpha_diff = np.subtract(n_alpha,n_1_alpha)
#
#            print('diff L2 norm: '+str(math.sqrt(np.sum(np.power(alpha_diff,2)))))