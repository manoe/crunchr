#!/bin/env python3

import numpy as np
import argparse as ap
import logging
logger = logging.getLogger(__name__)
import sys

if __name__ == '__main__':
    parser = ap.ArgumentParser(prog='gen_poisson_fail', description='Generate failing nodes',
                                     epilog=':-(')
    parser.add_argument('-s', '--seed', dest='seed', type=int, help='Seed to generate failing nodes')
    parser.add_argument('-n', '--nodes', dest='nodes', type=int, help='Number of nodes', required=True)
    parser.add_argument('-e', '--exclude', dest='exclude', type=int, help='Nodes to exclude', nargs='*')
    parser.add_argument('-l', '--lambda', dest='lambda_p', type=float, help='Lambda parameter', required=True)
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    node_list = list(np.arange(0, args.nodes))
    node_list = [i for i in node_list if i not in args.exclude]

    rng = np.random.default_rng(seed=args.seed)
    s = rng.poisson(args.lambda_p)
    logger.debug('Number of failing nodes: {}'.format(s))
    rng.shuffle(node_list)

    for i in node_list[:s]:
        print(i)
