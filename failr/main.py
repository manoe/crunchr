#!/bin/python3

import random
import yaml
import argparse
import operator


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='failr', description='Identify the next failing node', epilog=':-(')
    parser.add_argument('-f', '--file', dest='file', required=True)
    parser.add_argument('-b', '--basefile', dest='basefile')
    parser.add_argument('-H', '--hop', dest='hop', default=2, type=int)
    parser.add_argument('-d', '--debug', dest='debug', default=False, action='store_true')
    parser.add_argument('-r', '--random', dest='random', default=False, action='store_true')
    parser.add_argument('-s', '--seed', dest='seed', type=int)
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    stream = open(args.file, 'r')
    file_loader = yaml.safe_load(stream)

    node_list = {i['node']: i['forw_data_pkt_count'] for i in file_loader if i['hop'] > args.hop and i['state'] == 'live'}

    if args.basefile is not None:
        stream = open(args.basefile, 'r')
        base_loader = yaml.safe_load(stream)
        base_list = {i['node']: i['forw_data_pkt_count'] for i in base_loader if i['hop'] > args.hop}

        for i in base_list.keys():
            node_list[i] = node_list[i]-base_list[i]

    if args.debug:
        print(node_list)
        if args.basefile is not None:
            print(base_list)

    if args.random:
        n_l = list(node_list.keys())
        random.shuffle(n_l)
        print(n_l[0])
    else:
        print(max(node_list.items(), key=operator.itemgetter(1))[0])
