#!/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
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


def construct_graph(run):
    g_nw = nx.DiGraph()
    for i in run['loc_pdr']:
        g_nw.add_node(i['node'], pos=[i['x'], i['y']], state=i['state'])
        if 'routing_table' in i:
            for j in i['routing_table']:
                if 'node' in j:
                    g_nw.add_edge(i['node'], j['node'])
                elif 'next_hop' in j:
                    g_nw.add_edge(i['node'], j['next_hop'])
        elif 'engines' in i and len(i['engines']) > 0 and 'routing_table' in i['engines'][0]:
            for j in i['engines'][0]['routing_table']:
                if 'node' in j:
                    g_nw.add_edge(i['node'], j['node'])
                elif 'next_hop' in j:
                    g_nw.add_edge(i['node'], j['next_hop'])
    return g_nw


def calc_length_ratio(run, node):
    g_nw = construct_graph(run)
    try:
        path = nx.shortest_path(g_nw, source=node, target=0)
        print('path: '+str(path))
        c_length = 0
        t_length = calc_distance(g_nw.nodes[node]['pos'], g_nw.nodes[0]['pos'])
        for idx, i in enumerate(path[:-1]):
            c_length += calc_distance(g_nw.nodes[path[idx]]['pos'], g_nw.nodes[path[idx+1]]['pos'])
        return t_length / c_length
    except nx.NodeNotFound:
        pass
    except nx.exception.NetworkXNoPath:
        pass
    return -1


def calc_distance(p1, p2):
    return np.linalg.norm(np.subtract(p1, p2))


def calc_msr2mrp_routes(run):
    r_arr = {}
    for i in run['loc_pdr']:
        if 'engines' in i and len(i['engines']) > 0:
            r_arr[i['node']] = sum([len(i['routing_table']) if 'routing_table' in i else 0 for i in i['engines']])
    return r_arr


def calc_efmrp_routes(run):
    r_arr = {}
    for i in run['loc_pdr']:
        r = 0
        if 'routing_table' in i:
            for j in i['routing_table']:
                if j['origin'] == i['node'] and j['status'] == 'AVAILABLE':
                    r += 1
            r_arr[i['node']] = r
    return r_arr


def get_hop(run, node):
    for i in run['loc_pdr']:
        if i['node'] == node:
            if 'engines' in i and len(i['engines']) > 0:
                return i['engines'][0]['hop']
            if 'hop' in i:
                return i['hop']


def calc_length(run):
    g_nw = construct_graph(run)
    return [calc_distance(g_nw.nodes[n1[0]]['pos'], g_nw.nodes[n1[1]]['pos']) for n1 in g_nw.edges() if n1[1]]


def get_centrality(G):
    G_Cb = nx.betweenness_centrality(G, weight='weight', normalized=True)
    return sum([max(G_Cb.values())-i for i in G_Cb.values()])/(len(G)-1)


def get_msa(G):
    Gp = copy.deepcopy(G)
    Gp.remove_edges_from([i for i in DG.edges() if i[0] == 0])
    E = nx.algorithms.tree.Edmonds(Gp.reverse())
    return E.find_optimum(preserve_attrs=True, kind='max').reverse()


def pl_to_graph(pl):
    DG = nx.DiGraph()
    edges = [(i['node'], j['node'], 100 - j['PL']) for i in pl for j in i['neighbors'] if i['node'] != j['node']]
    print(edges)
    DG.add_weighted_edges_from(edges)
    return DG


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
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='debug mode on (aka. printf)')
    parser.add_argument('-S', '--seeds', dest='seeds', nargs='+', help='seeds')
    args = parser.parse_args()

    if args.shelve:
        shelve_in(args.file+'.dat')
    else:
        print('Creating file: ' + args.file+'.dat')
#        loader = yaml.safe_load(open(args.file, 'r'))
        res = []

#        for run in loader['runs']:
        for seed in args.seeds:
            run = yaml.safe_load(open(args.file.replace('_pdr.yaml', '')+'_seed_'+str(seed)+'/pdr.yaml', 'r'))
            pl = yaml.safe_load(open(args.file.replace('_pdr.yaml', '')+'_seed_'+str(seed)+'/avg_pl.yaml', 'r'))
            pl_g = pl_to_graph(pl)

            centrality = {}
            centrality['pl'] = get_centrality(pl_g)
            centrality['msa'] = get_centrality(get_msa(pl_g))
            centrality['proto'] = get_centrality(construct_graph(run))

            loc = gen_node_loc(run)
            conn = gen_node_conn(run)
            l_arr = calc_length(run)



            hop = {i['node']: get_hop(run, i['node']) for i in run['pdr']}
            lratio = {i['node']: calc_length_ratio(run, i['node']) for i in run['pdr']}
            pdr = gen_node_pdr(run)
            route_arr = []
            if run['protocol'] == 'msr2mrp':
                route_arr = calc_msr2mrp_routes(run)
            elif run['protocol'] in ['efmrp', 'smrp']:
                route_arr = calc_efmrp_routes(run)
            if args.debug:
                print(conn)
                print(route_arr)
                print(l_arr)
                print(hop)
                print(lratio)
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
                if args.debug:
                    print('=====================')
                if err > th:
                    if args.debug:
                        print('Error higher: '+str(err))
                    r_idx_new = int(r_idx_right-((r_idx_right-r_idx)/2))
                    r_idx_left = r_idx
                elif err <= th:
                    if area < 1.0:
                        if args.debug:
                            print('Done - error reached. Error: '+str(err))
                        break
                    else:
                        if args.debug:
                            print('Error lower: '+str(err))
                        r_idx_new = int(r_idx_left+(r_idx-r_idx_left)/2)
                        r_idx_right = r_idx
                if args.debug:
                    print('Index: ' + str(r_idx))
                    print('Area:  ' + str(area))
                    print('New index: ' + str(r_idx_new))
                    print('Idx left: ' +str(r_idx_left))
                    print('Idx right: ' + str(r_idx_right))

                if r_idx_new == r_idx:
                    if args.debug:
                        print('Done - recurring index. Error: ' + str(err))
                    break
                else:
                    r_idx = r_idx_new
            if args.debug:
                print('Index: ' + str(r_idx))
                print('Area:  ' + str(area))
                print('Value: ' + str(r_arr[r_idx]))

            res.append({'seed': run['seed'], 'pdr': calc_pdr(run), 'dc-pdr': calc_dc_pdr(run), 'radius': r_arr[r_idx],
                       'l_avg': np.average(l_arr), 'l_std': np.std(l_arr), 'l_arr': l_arr, 'route_arr': route_arr, 'lratio': lratio, 'hop': hop, 'n-pdr': pdr})

        shelve_out(args.file+'.dat', ['res', 'circles', 'area', 'c', 'xx', 'yy', 'args'])


    if args.plot is True:
#    if True:
        fig, ax = plt.subplots(nrows=1,ncols=2)

        x_p_coord = [i['pdr'] for i in res]
        x_dp_coord = [i['dc-pdr'] for i in res]
        y_coord = [i['radius'] for i in res]
        ax[0].scatter(x_p_coord, y_coord, s=10)
        ax[1].scatter(x_dp_coord, y_coord, s=10)
        ax[0].grid(True)
        ax[1].grid(True)
        ax[0].set_title('PDR')
        ax[1].set_title('DC-PDR')


        # Printing the graph
        fig.suptitle(args.file)
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

