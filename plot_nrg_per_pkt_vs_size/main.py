#!/bin/python3

import yaml
import argparse
import matplotlib.pyplot as plt
import numpy as np
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_nrg_per_pkt_vs_size',
                                     description='Plot energy per received packet vs network size', epilog=':-(')
    parser.add_argument('-i', '--image',
                        action='store_true', dest='image')
    parser.add_argument('-c', '--count', action='store', dest='count', default=10, type=int)
    parser.add_argument('-p', '--percent', action='store', dest='percent', default='0.8',
                        help='Init percentage', type=float)
    parser.add_argument('-s', '--size', action='store', dest='size', help='network size, n x n', nargs='+', type=int)
    parser.add_argument('-d', '--data', action='store_true', dest='data')
    parser.add_argument('-e', '--errorbar', action='store_true')
    parser.add_argument('-l', '--legend', nargs='+', type=str, dest='legend', action='store')
    parser.add_argument('-f', '--filename', help='filename prefixes', nargs='+', required=True)

    args = parser.parse_args()

    args.size.sort()

    files = args.filename

    y_nrg = {}
    y_nrg_std = {}
    y_time = {}
    y_time_std = {}

    if os.path.isfile('out.bin'):
        print('Results present, reading in')
        shelve_in('out.bin')
    else:
        for filename in files:
            y_nrg[filename] = {}
            y_nrg_std[filename] = {}

            for s in args.size:
                stream = open(filename+'_'+str(s)+'.yaml', 'r')
                node = s**2-1

                print('Processing '+filename+' with size '+str(s))

                loader = yaml.safe_load(stream)

                pkt_list = {}
                fail = 0

                data = [j['pkt_list'][-1]['energy']/len(j['pkt_list']) for j in loader['runs']]

                y_nrg[filename][s] = np.average(data)
                y_nrg_std[filename][s] = np.std(data)
        shelve_out('out.bin', ['y_nrg','y_nrg_std'])


    width = 0.8
    bar_width = width / len(y_nrg)

    idx = 0
    if args.errorbar:
        for idx, data in enumerate(y_nrg):
            plt.errorbar([x + idx*bar_width-width/2 for x in range(len(args.size))], list(y_nrg[data].values()),
                         list(y_nrg_std[data].values()), linestyle='None')
    else:
        for idx, i in enumerate(y_nrg):
            bc = plt.bar([x + idx*bar_width-width/2 for x in range(len(args.size))], list(y_nrg[i].values()), bar_width)
            bl = plt.bar_label(bc, label=args.size, fmt="%.2g", rotation=45)
#            for j in bl:
#                j.set_font_properties({'size': 'small'})
#            idx += 1

    #plt.title('Consumed energy per packet vs. size')
    plt.xticks(range(len(args.size)), labels=[x**2 for x in args.size])
    ticks = list(plt.yticks()[0])
    ticks.append(ticks[-1]+ticks[-1]-ticks[-2])
    
    plt.yticks(ticks)
    if args.legend is not None:
        plt.legend(args.legend)
    else:
        plt.legend(list(y_nrg.keys()))
    plt.xlabel('Node number')
    plt.ylabel('Energy per message (J/msg)')
    plt.grid(axis='y')
    plt.show()
    exit(0)
