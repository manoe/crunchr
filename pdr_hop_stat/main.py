#!/bin/python3
import errno

import yaml
import matplotlib.pyplot as plt
import numpy as np
import sys
import networkx
# import scipy as sp


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        stream = open(sys.argv[1], 'r')
    else:
        try:
            stream = open('shmrp_meas_rreq_5.yaml', 'r')
        except IOError as e:
            print(e)
            exit(e.errno)
        except Exception as e:
            print(e)
            exit(2)

    loader = yaml.safe_load(stream)

    runs = loader['runs']
    loc_pdr_hist = []

    for run in runs:
        # print(run['seed'])
        pdr_arr = list(run['pdr'].values())[1:]
        run['avg_pdr'] = np.average(pdr_arr)
        run['std_pdr'] = np.std(pdr_arr)
        run['disconn'] = pdr_arr.count(0)
        # print(run['std_pdr'])

        loc_pdr = []
        for i in run['loc_pdr']:
            if 'routing_table' in i:
                for j in i['routing_table']:
                    pdr = 0
                    for k in run['loc_pdr']:
                        if k['node'] == j['node'] and 'recv_table' in k:
                            for l in k['recv_table']:
                                if l['node'] == i['node']:
                                    pdr = l['pkt_count']/j['pkt_count']
                                    loc_pdr.append(pdr)

        run['avg_loc_pdr'] = np.average(loc_pdr)
        loc_pdr_hist.extend(loc_pdr)

    avg_pdr = []
    std_pdr = []
    disconn = []
    avg_loc_pdr = []

    for run in runs:
        avg_pdr.append(run['avg_pdr'])
        std_pdr.append(run['std_pdr'])
        disconn.append(run['disconn'])
        avg_loc_pdr.append(run['avg_loc_pdr'])
    print('Average pdr:     ' + str(np.average(avg_pdr)))
    print('Average std:     ' + str(np.average(std_pdr)))
    print('Average disconn: ' + str(np.average(disconn)))
    print('Average loc pdr: ' + str(np.average(avg_loc_pdr)))

    bins = np.arange(0, 1.1, 0.1)
    plt.hist(loc_pdr_hist, bins)
    plt.show()
