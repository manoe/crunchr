#!/bin/env python3

import scipy.stats as sp


def generate(e_n):
    in_list = [[i] for i in list(range(e_n, 0, -1))]
    n = e_n
    done = False

    out_list = []

    while not done:
        for i in in_list:
            if n-sum(i) > 0:
                for j in list(range(i[-1], 0, -1)):
                    if sum(i)+j <= n:
                        out_list.append(i+[j])
            else:
                out_list.append(i)

        done = True
        for i in out_list:
            if sum(i) < n:
                done = False

        in_list = out_list
        out_list = []

    return in_list

if __name__ == '__main__':
    e_arr = []
    for i in range(2, 9, 1):
        print('Edge count: '+str(i))
        for j in generate(i):
            e = sp.entropy([k / sum(j) for k in j], base=2) / sp.entropy([1 / i for k in range(i)], base=2)
            e_arr.append(e)
            print(str(j)+': '+str(e))

    e_arr.sort()
    print(e_arr)

    for i in range(0, 14, 1):
        len(generate(i))

