#!/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import argparse
import yaml
import math
import shelve as sh


def shelve_out(filename, keys):
    my_shelf = sh.open(filename, 'n')  # 'n' for new
    for key in keys:
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
    my_shelf = sh.open(filename)
    for key in my_shelf:
        globals()[key] = my_shelf[key]
    my_shelf.close()

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


def calc_pdr(run):
    pdrs = []
    for node in run['pdr']:
        if 'report_pdr' in node:
            pdrs.append(node['report_pdr'])
    return np.average(pdrs)


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
    parser.add_argument('-t', '--threshold', dest='threshold', action='store', type=float, help='The error threshold', default=0.01)
    parser.add_argument('-p', '--plot', dest='plot', action='store_true', help='Let\'s plot')
    parser.add_argument('-s', '--shelve', dest='shelve', action='store_true',
                        help='use the pattern blabla_px_py_babla.yaml')
    args = parser.parse_args()

    if args.shelve:
        shelve_in(args.file+'.dat')
    else:
        print('Opening file: ' + args.file)
        loader = yaml.safe_load(open(args.file, 'r'))
        res = []
        for run in loader['runs']:
            loc = gen_node_loc(run)
            conn = gen_node_conn(run)
            print(conn)
            x = np.linspace(0, args.length, 300)
            y = np.linspace(0, args.length, 300)
            # 100:  0.4119
            # 200:  0.41235
            # 300:  0.4096222222222222
            # 500:  0.408752
            # 1000: 0.408165
            xx, yy = np.meshgrid(x, y)
            err = 1.0
            th  = args.threshold
            r_min = 0
            r_max = math.sqrt(2)*args.length
            r_arr = np.linspace(r_min, r_max, 200)
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
                        print('Done - error reached. Error: '+str(err))
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
                    print('Done - recurring index. Error: ' + str(err))
                    break
                else:
                    r_idx = r_idx_new
            print('Index: ' + str(r_idx))
            print('Area:  ' + str(area))
            print('Value: ' + str(r_arr[r_idx]))

            res.append({'seed': run['seed'], 'pdr': calc_pdr(run), 'dc-pdr': calc_dc_pdr(run), 'radius': r_arr[r_idx]})

        shelve_out(args.file+'.dat',['res', 'circles', 'area', 'c', 'xx', 'yy', 'args'])

    print(res)
    if args.plot is True:
    fig, ax = plt.subplots(nrows=1,ncols=2)

    x_p_coord = [i['pdr'] for i in res]
    x_dp_coord = [i['dc-pdr'] for i in res]
    y_coord = [i['radius'] for i in res]
    ax[0].scatter(x_p_coord, y_coord, s=10)
    ax[1].scatter(x_dp_coord, y_coord, s=10)
    ax[0].set_title('PDR')
    ax[1].set_title('DC-PDR')


    # Printing the graph
    plt.title(args.file)
    plt.show()



#        fig, ax = plt.subplots()
#        ax.set(xlim=(0, args.length), ylim=(0, args.length))
#        colors = list(map(lambda x: {True: 'b', False: 'w'}[x], c))
#        plt.scatter(np.ravel(xx), np.ravel(yy), c=colors)
#        plt.title(f'Area: {area}')
#        for c in circles:
#            a_circle = plt.Circle((c.x, c.y), c.radius, color='r', linewidth=1, fill=False)
#            ax.add_artist(a_circle)
#        ax.add_patch(plt.Rectangle((0, 0), args.length, args.length, color="k", linewidth=1, fill=False))#

#        # Printing the graph
#        plt.show()

        # plotting circles and a square from (0,0) to (1,1)

