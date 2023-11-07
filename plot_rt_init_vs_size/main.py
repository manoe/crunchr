#!/bin/python3

import yaml
import argparse
import matplotlib.pyplot as plt
import sys
import numpy as np


def check_status(stats, node, percent):
    if len([x for x in stats.values() if x is True])/node >= percent:
        return True
    return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_rt_init_vs_size', description='Plot protocol init time vs network size', epilog=':-(')
    parser.add_argument('-i', '--image',
                        action='store_true', dest='image')
    parser.add_argument('-p', '--percent', action='store', dest='percent', default='0.8',
                        help='Init percentage', type=float)
    parser.add_argument('-s', '--size', action='store', dest='size', help='network size, n x n', nargs='+', type=int)
    parser.add_argument('-d', '--data', action='store_true', dest='data')
    parser.add_argument('-e', '--errorbar', action='store_true')

    parser.add_argument('filename', help='filename prefixes', nargs='+')

    args = parser.parse_args()

    args.size.sort()

    files = args.filename

    y_nrg = {}
    y_nrg_std = {}
    y_time = {}
    y_time_std = {}

    size_arr = args.size+args.size

    size_arr = [int(x) for x in size_arr]

    idx = 0

    for filename in files:
        y_nrg[filename] = {}
        y_time[filename] = {}
        y_nrg_std[filename] = {}
        y_time_std[filename] = {}

        for s in args.size:
            stream = open(filename+'_'+str(s)+'.yaml', 'r')
            node = s**2-1

            print('Processing '+filename+' with size '+str(s))

            loader = yaml.safe_load(stream)

            state_list = {}
            fail = 0
            data = []

            for j in loader['runs']:
                state_list = {}
                for i in j['state_list']:
                    if i['state'] == 'WORK':
                        state_list[i['node']] = True
                    if check_status(state_list, node, args.percent):
                        data.append({'timestamp': i['timestamp'],
                                     'energy':    i['total_energy'],
                                     'percent':  args.percent})
                        if args.data:
                            print(str(i['timestamp']) + '#' + str(l) + '#' + str(i['energy']))
                        else:
                            print(str(args.percent) + ' of active nodes reached at ' + str(i['timestamp'])+' with ' + str(i['energy']) + ' J of energy')
                        fail -= 1
                        break
                fail += 1

            if fail > 0:
                print('Init criteria not met x'+str(fail)+' times')

            y_nrg[filename][s] = np.average([x['energy'] for x in data if x['percent'] == args.percent])
            y_nrg_std[filename][s] = np.std([x['energy'] for x in data if x['percent'] == args.percent])
            y_time[filename][s] = np.average([x['timestamp'] for x in data if x['percent'] == args.percent])
            y_time_std[filename][s] = np.std([x['timestamp'] for x in data if x['percent'] == args.percent])
            idx += 1

#    y_efmrp_nrg=list(y_nrg.values())[:len(args.size)]
#    y_shmrp_nrg=list(y_nrg.values())[len(args.size):]

#    y_efmrp_time = list(y_time.values())[:len(args.size)]
#    y_shmrp_time = list(y_time.values())[len(args.size):]

    plt.subplot(2,1,1)

    width = 0.8
    bar_width = width / len(y_nrg)

    idx = 0
    if args.errorbar:
        for idx, data in enumerate(y_nrg):
            plt.errorbar([x + idx*bar_width-width/2 for x in range(len(args.size))], list(y_nrg[data].values()),
                         list(y_nrg_std[data].values()), linestyle='None')
    else:
        for i in y_nrg:
            bc = plt.bar([x + idx*bar_width-width/2 for x in range(len(args.size))] , y_nrg[i].values(), bar_width)
            plt.bar_label(bc, label=args.size)
            idx += 1

    plt.title('Consumed energy vs. size')
    plt.xticks(range(len(args.size)), labels=args.size)

    plt.subplot(2,1,2)

    idx = 0
    for i in y_nrg:
        bc = plt.bar([x + idx*bar_width-width/2 for x in range(len(args.size))] , y_time[i].values(), bar_width)
        plt.bar_label(bc, label=args.size)
        idx += 1

    plt.title('Elapsed time vs. size')
    plt.xticks(range(len(args.size)), labels=args.size)
    plt.legend(y_time.keys())
    plt.show()
    exit(0)
