#!/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import argparse
import math
import logging
logger = logging.getLogger(__name__)
import sys
import copy
from collections import deque

def calc_pd_log(dist):
    logger.debug('dist={}'.format(dist))
    res = 1.0 / (1.0 + math.exp(args.alpha*(dist-args.d0)))
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

def calc_e_p(nodes):
    res = 0.0
    for node in nodes[1:]:
        res += calc_b(calc_dist(node))
    return res

def calc_beta(alpha_n, alpha_n_1):
    delta = alpha_n-alpha_n_1
    beta = np.zeros(shape=alpha_n.shape)
    for v in range(1,args.node):
        m_v=delta[v,:].sum()
        for p in range(1,args.node):
            beta[v,p]=delta[v,p]/(m_v+args.epsilon)
    return beta

def calc_lambda(alpha, nodes):
    n = alpha.shape[0]
    p_border = [calc_b(calc_dist(nodes[u])) if u != 0 else 0.0 for u in range(n)]
    lambda_arr = np.zeros(shape=(n))
    for v in range(1, n):
        lambda_arr[v] = math.fsum(p_border[u] * alpha[v, u] for u in range(1, n))
    return lambda_arr

def print_alpha_matrix(matrix):
    n = matrix.shape[0]
    row_labels = ['Node {}'.format(v) for v in range(n)]
    col_labels = ['Path {}'.format(p) for p in range(n)]
    row_hdr_w = max(len(s) for s in row_labels) + 2
    col_w = max(max(len(s) for s in col_labels), len('0.0000')) + 2
    header = ' ' * row_hdr_w + ''.join(c.rjust(col_w) for c in col_labels)
    print(header)
    for v in range(n):
        row = row_labels[v].ljust(row_hdr_w)
        row += ''.join('{:.4f}'.format(matrix[v, p]).rjust(col_w) for p in range(n))
        print(row)

def build_nodes(distance):
    nodes = {}
    for i in range(args.x):
        for j in range(args.y):
            if i * args.y + j < args.node:
                nodes[i * args.y + j] = {'x': i * distance, 'y': j * distance}
    return nodes

def calc_alpha(distance):
    nodes = build_nodes(distance)

    alpha_queue = deque()
    alpha_queue.appendleft(np.zeros(shape=(args.node, args.node)))

    first = np.zeros(shape=(args.node, args.node))
    for i in range(1, args.node):
        first[i, i] = calc_b(calc_dist(nodes[i]))
    a_queue = deque()
    o_queue = deque()

    a_queue.appendleft(np.zeros(shape=(args.node)))
    o_queue.appendleft(np.zeros(shape=(args.node)))

    a_arr = [0.0]
    o_arr = [0.0]
    for v in range(1, args.node):
        a = calc_pd(calc_dist(nodes[v]))
        o = calc_pd(calc_dist(nodes[v]))
        a_arr.append(a)
        o_arr.append(o)
    a_queue.appendleft(a_arr)
    o_queue.appendleft(o_arr)

    alpha_queue.appendleft(first)
    beta = copy.deepcopy(first)

    for i in range(2, args.iter):

        alpha = np.zeros(shape=(args.node, args.node))

        a_arr = [0.0]
        o_arr = [0.0]
        for v in range(1, args.node):
            a_prod_body = [ 1 - math.fsum(beta[u,:]) * calc_pd(calc_dist_2( nodes[u],nodes[v] )) for u in range(1,args.node) if u != v ]
            a = 1 - math.prod(a_prod_body)
            a_arr.append(a)
            o = (1 - math.fsum([ o_elem[v] for o_elem in o_queue])) * a
            o_arr.append(o)

            for p in range(1, args.node):
                prod_body = [ 1 - beta[u,p] * calc_b(calc_dist_2( nodes[u],nodes[v] )) for u in range(1, args.node) if u != v ]
                alpha[v, p] = alpha_queue[0][v,p] + o * (1 - alpha_queue[0][v,p]) * (1 - math.prod(prod_body) )
        alpha_queue.appendleft(alpha)
        o_queue.appendleft(o_arr)
        a_queue.appendleft(a_arr) # felesleges
        beta = calc_beta(alpha_queue[0],alpha_queue[1])

    return alpha_queue[0], nodes

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='r2mrp_analytic', description='Calculate R2MRP-specific data analytically', epilog=':-(')
    parser.add_argument('-d', '--data', dest='data', choices=['e_p', 'alpha', 'graph'], help='Data that should be calculated', default='alpha')
    parser.add_argument('-n', '--node-num', dest='node', type=int, help='Number of nodes', default=100)
    parser.add_argument('-x', '--x-num', dest='x', type=int, help='Number of grid points along axis X', default=10)
    parser.add_argument('-y', '--y-num', dest='y', type=int, help='Number of grid points along axis Y', default=10)
    parser.add_argument('-l', '--log-level', dest='log_level', choices=['debug','info','none'], default='none', help='Log level')
    parser.add_argument('-gd','--grid-distance', dest='grid_distance', type=float, nargs='+', help='Grid cell distance(s) in meters; multiple values are swept for graphs', default=[20])
    parser.add_argument('-q', '--qos', dest='qos', type=float, help='QoS filter value', default=0.8)
    parser.add_argument('-nt', '--num-test', dest='nt', type=int, help='Number of link test messages', default=10)
    parser.add_argument('-rd', '--ref_dist', dest='d0', type=float, help='Reference distance', default=1)
    parser.add_argument('-a', '--alpha', dest='alpha', type=float, help='Attenuation coefficient', default=2.5)
    parser.add_argument('-i', '--iter', dest='iter', type=int, help='Number of iterations, if alpha is calculated', default=100)
    parser.add_argument('-e', '--epsilon', dest='epsilon', type=float, help='Epsilon',
                        default=0.00001)
    parser.add_argument('-r', '--radio', dest='radio', choices=['log', 'div'], help='Radio channel',
                        default='log')
    parser.add_argument('-g', '--graph', dest='graph', choices=['spof', 'nw_e_v', 'hop', 'crit'],
                        default='spof', help='Graph to plot (used when -d graph)')

    args = parser.parse_args()


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

    match args.data:
        case 'e_p':
            print('Calculating E[P], expected number of paths:')
            nodes = build_nodes(args.grid_distance[0])
            logger.info('Node array done, size:{}'.format(len(nodes))+' on a field of {}'.format(args.x)+'x{}'.format(args.y))
            print('E[P]={}'.format(calc_e_p(nodes)))
        case 'alpha':
            print('Calculating alpha values')
            alpha, nodes = calc_alpha(args.grid_distance[0])
            print('Last alpha matrix:')
            print_alpha_matrix(alpha)
        case 'graph':
            match args.graph:
                case 'spof':
                    p_c0 = []
                    p_c1 = []
                    p_c2 = []
                    for gd in args.grid_distance:
                        alpha, nodes = calc_alpha(gd)
                        lambda_arr = calc_lambda(alpha, nodes)
                        p_c0.append(np.mean(np.exp(-lambda_arr[1:])))
                        p_c1.append(np.mean(lambda_arr[1:] * np.exp(-lambda_arr[1:])))
                        p_c2.append(np.mean(1 - np.exp(-lambda_arr[1:]) * (1 + lambda_arr[1:])))

                    plt.figure()
                    plt.plot(args.grid_distance, p_c0, marker='o', label='P(C=0)')
                    plt.plot(args.grid_distance, p_c1, marker='o', label='P(C=1)')
                    plt.plot(args.grid_distance, p_c2, marker='o', label='P(C>=2)')
                    plt.xlabel('Grid distance [m]')
                    plt.ylabel('Probability')
                    plt.legend()
                    plt.savefig('spof.png')
                    print('Saved spof.png')
                case 'nw_e_v':
                    print('Graph: nw_e_v')
                case 'hop':
                    print('Graph: hop')
                case 'crit':
                    print('Graph: crit')
