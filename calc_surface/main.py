#!/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import argparse
import yaml
import math

# Making a class circle and initializing it with its centre and radius
class circle:
    def __init__(self,radius,x,y):
        self.radius = radius
        self.x = x
        self.y = y

# Finding point that lies inside the circle
    def exist_in_circle(self, x1, y1):
        if (self.x-x1)*(self.x-x1)+(self.y-y1)*(self.y-y1) <= self.radius*self.radius:
            return True
        else:
            return False


def calc_connr(run):
    return len([node['node'] for node in run['pdr'] if 'report_pdr' in node and node['report_pdr'] != 0])/len([node['node'] for node in run['pdr'] if 'report_pdr' in node])


def gen_node_conn(run):
    is_conn = lambda n: 'report_pdr' in n and n['report_pdr'] != 0 or n['node'] == 0
    return {node['node']: is_conn(node) for node in run['pdr']}

def gen_node_loc(run):
    return {i['node']: [i['x'], i['y']] for i in run['loc_pdr']}


def gen_node_pdr(run):
    return {i['node']: i['report_pdr'] for i in run['pdr'] if 'report_pdr' in i}


def calc_dc_pdr(run):
    loc = gen_node_loc(run)
    pdr = gen_node_pdr(run)
    d_max = max([np.linalg.norm(i) for i in loc.values()])
    return np.average([np.linalg.norm(loc[i])/d_max*pdr[i] for i in pdr.keys()])


def in_area(point):
    exist = [c.exist_in_circle(*point) for c in circles]
    return exist.count(True) > 0


# initializing plt of matplotlib
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='calc_surface', description='Calculate coverage surface, yeah', epilog=':-(')
#    parser.add_argument('-px', '--param-x', dest='param_x', action='store', nargs='+', type=str, required=True)
#    parser.add_argument('-py', '--param-y', dest='param_y', action='store', nargs='+', type=str, required=True)
#    parser.add_argument('-x', '--exclude', dest='exclude', nargs='+', type=int, help='Exclude nodes from calculation')
#    parser.add_argument('-i', '--include', dest='include', nargs='+', type=int,
#                        help='Include only these nodes in calculation')
#    parser.add_argument('-d', '--no_dead', dest='no_dead', action='store_true')
#    parser.add_argument('-ex', '--external', dest='external', action='store_true')
#    parser.add_argument('-e', '--event', dest='event', action='store_true')
#    parser.add_argument('-tx', '--title-x', dest='title_x', action='store', type=str, default='X')
#    parser.add_argument('-ty', '--title-y', dest='title_y', action='store', type=str, default='Y')
    parser.add_argument('-f', '--file', dest='file', help='use the pattern blabla_px_py_babla.yaml', required=True)
    parser.add_argument('-l', '--length', dest='length', help='Side length of the area', default=160, type=float)
    parser.add_argument('-r', '--radius', dest='radius', help='Radius ', default=5, type=float)
#    parser.add_argument('-t', '--tail', dest='tail', action='store', type=float, help='The tail threshold', default=0.0)
#    parser.add_argument('-p', '--plot', dest='plot', action='store', choices=['pdr', 'connr', 'dc_pdr', 'd_p'],
#                        help='Kind of the plot')
#    parser.add_argument('-s', '--shelve', dest='shelve', action='store_true',
#                        help='use the pattern blabla_px_py_babla.yaml')
    args = parser.parse_args()

    print('Opening file: ' + args.file)
    loader = yaml.safe_load(open(args.file, 'r'))

    loc = gen_node_loc(loader['runs'][0])

    conn = gen_node_conn(loader['runs'][0])
    print(conn)

    fig, ax = plt.subplots()
    ax.set(xlim=(0, args.length), ylim=(0, args.length))

    x = np.linspace(0, args.length, 300)
    y = np.linspace(0, args.length, 300)
    # 100:  0.4119
    # 200:  0.41235
    # 300:  0.4096222222222222
    # 500:  0.408752
    # 1000: 0.408165

    xx, yy = np.meshgrid(x, y)
    print(x.shape, y.shape, xx.shape, yy.shape)

    err = 1.0
    th  = 0.01
    r_min = 0
    r_max = math.sqrt(2)*args.length
    r_arr = np.linspace(r_min, r_max, 100)
    r_idx = len(r_arr) - 1
    r_idx_left = 0
    r_idx_right = len(r_arr) - 1
    while True:
        circles = [circle(r_arr[r_idx], loc[i][0], loc[i][1]) for i in loc.keys() if conn[i]]
        c = [in_area((x,y)) for x, y in zip(np.ravel(xx), np.ravel(yy))]
        area = sum(c) / len(c)
        err = 1.0 - area
        print('=====================')
        if err > th:
            print('Error higher: '+str(err))
            r_idx_new = int(r_idx_right-((r_idx_right-r_idx)/2))
            r_idx_left = r_idx
        elif err <= th:
            if area < 1.0:
                print('Done')
                break
            else:
                print('Error lower: '+str(err))
                r_idx_new = int(r_idx_left+(r_idx-r_idx_left)/2)
                r_idx_right = r_idx
        print('Index: ' + str(r_idx))
        print('Area:  ' + str(area))
        print('New index: ' + str(r_idx_new))
        print('Idx left: ' +str(r_idx_left))
        print('Idx right: ' + str(r_idx_right))

        if r_idx_new == r_idx:
            break
        else:
            r_idx = r_idx_new


    colors = list(map(lambda x: {True: 'b', False: 'w'}[x], c))
    plt.scatter(np.ravel(xx), np.ravel(yy), c=colors)
    plt.title(f'Area: {area}')


    # plotting circles and a square from (0,0) to (1,1)
    for c in circles:
        a_circle = plt.Circle((c.x, c.y), c.radius, color='r', linewidth=1, fill=False)
        ax.add_artist(a_circle)
    ax.add_patch(plt.Rectangle((0, 0), args.length, args.length, color="k", linewidth=1, fill=False))

    # Printing the graph
    plt.show()
