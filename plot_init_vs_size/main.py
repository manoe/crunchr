#!/bin/python3

import yaml
import argparse
import matplotlib.pyplot as plt
import sys
import numpy as np

#from matplotlib.ticker import FormatStrFormatter

import os.path
import shelve

def shelve_out(filename, keys):
    my_shelf = shelve.open(filename, 'n')  # 'n' for new
    for key in keys:
        print('key: '+str(key))
        try:
            my_shelf[key] = globals()[key]
        except TypeError:
            #
            # __builtins__, my_shelf, and imported modules can not be shelved.
            #
            print('ERROR shelving: {0}'.format(key))
        except KeyError:
            print('ERROR shelving: {0}'.format(key))
        except:
            print('ERROR')
    my_shelf.close()


def shelve_in(filename):
    my_shelf = shelve.open(filename)
    for key in my_shelf:
        globals()[key] = my_shelf[key]
    my_shelf.close()


def check_status(stats, node, percent, count):
    decision = {}
    for i in stats:
        if stats[i] >= count:
            decision[i] = True
    if len(decision)/node >= percent:
        return True
    return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_init_vs_size', description='Plot protocol init time vs network size', epilog=':-(')
    parser.add_argument('-i', '--image',
                        action='store_true', dest='image')
    parser.add_argument('-c', '--count', action='store', dest='count', default=10, type=int)
    parser.add_argument('-p', '--percent', action='store', dest='percent', default='0.8',
                        help='Init percentage', type=float)
    parser.add_argument('-s', '--size', action='store', dest='size', help='network size, n x n', nargs='+', type=int)
    parser.add_argument('-d', '--data', action='store_true', dest='data')
    parser.add_argument('-e', '--errorbar', action='store_true')
    parser.add_argument('-l', '--legend', nargs='+', type=str, dest='legend', action='store')
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

    if os.path.isfile('out.bin'):
        print('Results present, reading in')
        shelve_in('out.bin')
    else:
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

                pkt_list = {}
                fail = 0
                data = []

                for k in [args.percent]:
                    for j in loader['runs']:
                        pkt_list = {}
                        for i in j['pkt_list']:
                            if i['source'] in pkt_list:
                                pkt_list[i['source']] += 1
                            else:
                                pkt_list[i['source']] = 1
                            if check_status(pkt_list, node, k, args.count):
                                data.append({'timestamp': i['timestamp'],
                                             'energy':    i['energy'],
                                             'percent':  k})
                                if args.data:
                                    print(str(i['timestamp']) + '#' + str(l) + '#' + str(i['energy']))
                                else:
                                    print(str(k) + ' of active nodes reached at ' + str(i['timestamp'])+' with criteria of '
                                          + str(args.count) + ' packets and ' + str(i['energy']) + ' J of energy')
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
        shelve_out('out.bin', ['y_nrg', 'y_nrg_std', 'y_time', 'y_time_std'])

#    y_efmrp_nrg=list(y_nrg.values())[:len(args.size)]
#    y_shmrp_nrg=list(y_nrg.values())[len(args.size):]

#    y_efmrp_time = list(y_time.values())[:len(args.size)]
#    y_shmrp_time = list(y_time.values())[len(args.size):]

    plt.subplot(2,1,1)

    width = 0.8
    bar_width = width / len(y_nrg)
    plt.yscale("log")
    idx = 0
    if args.errorbar:
        for idx, data in enumerate(y_nrg):
            plt.errorbar([x + idx*bar_width-width/2 for x in range(len(args.size))], list(y_nrg[data].values()),
                         list(y_nrg_std[data].values()), linestyle='None')
    else:
        for i in y_nrg:
            bc = plt.bar([x + idx*bar_width-width/2 for x in range(len(args.size))] , y_nrg[i].values(), bar_width)
            plt.bar_label(bc, label=args.size, rotation=45, fmt="%.0f")
            idx += 1

    plt.grid(axis='y')
    plt.title('(a)', loc='left')
    plt.ylabel('Energy (J)')
    plt.xticks(range(len(args.size)), labels=[x**2 for x in args.size])

    ticks = list(plt.yticks()[0])
    ticks.append(ticks[-1] + ticks[-1] - ticks[-2])

    plt.yticks(ticks)

    plt.xlabel('Node number')
    #plt.ylabel('J')
    if args.legend is not None:
        plt.legend(args.legend, ncol=2, loc='upper left')
    else:
        plt.legend(list(y_nrg.keys()))
    plt.subplot(2,1,2)
    plt.grid(axis='y')
    idx = 0

    plt.yscale("log")

    for i in y_nrg:
        bc = plt.bar([x + idx*bar_width-width/2 for x in range(len(args.size))] , y_time[i].values(), bar_width)
        plt.bar_label(bc, label=args.size, rotation=45, fmt="%.0f")
        idx += 1

    plt.title('(b)', loc='left')
    plt.ylabel('Time (s)')
    plt.xticks(range(len(args.size)), labels=[x**2 for x in args.size])
    ticks = list(plt.yticks()[0])
    ticks.append(ticks[-1] + ticks[-1] - ticks[-2])

    plt.yticks(ticks)
    plt.xlabel('Node number')
    #plt.ylabel('s')
    plt.show()
    exit(0)
