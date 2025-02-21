#!/bin/env python3
import matplotlib.animation as anm
import yaml
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import argparse
import logging
from enum import Enum

logger = logging.getLogger(__name__)
import sys

from matplotlib import rcParams

rcParams['font.family'] = ['serif']
rcParams['font.serif'] = ['Times New Roman']


#enum CellState {
#    NO_FUEL,
#    NOT_IGNITED,
#    BURNING,
#    BURNED_DOWN
#};

#Hint: /home/uveges/devCastalia/Castalia/Simulations/shmrp_ff_event

class CellState(Enum):
    NO_FUEL = 0
    NOT_IGNITED = 1
    BURNING = 2
    BURNED_DOWN = 3


def map_value(value):
    alpha = 128
    logger.debug(int(value))
    match CellState(int(value)):
        case CellState.NO_FUEL:
            return 0, 0, 0, alpha
        case CellState.NOT_IGNITED:
            return 255, 255, 255, alpha
        case CellState.BURNING:
            return 201, 14, 14, alpha
        case CellState.BURNED_DOWN:
            return 122, 89, 62, alpha
        case _:
            raise ValueError("Invalid cell state")


def gen_frame(plane):
    logger.debug('Array\'s shape (y,x): ' + str((len(plane), len(str(plane[0]['y'])))))
    frame = np.ndarray(shape=(len(plane), len(str(plane[0]['y'])), 4), dtype=np.uint8)
    for idx, i in enumerate(plane):
        logger.debug('Array\'s idx: ' + str(idx))
        frame[idx, :, :] = [map_value(j) for j in str(i['y'])]
    logger.debug(frame)
    return frame

def construct_graph(run):
    nw = nx.MultiDiGraph()
    for node in run:
        nw.add_node(node['node'], master=node['master'], pos=[node['x'], node['y']], state=node['state'])
        if 'engines' in node:
            roles = []
            for engine in node['engines']:
                if 'routing_table' in engine and node['state'] == 'ALIVE':
                    for re in engine['routing_table']:
                        pathid = [pe['pathid'] for pe in re['pathid']]
                        if engine['role'] == 'external':
                            secl = False
                            for k in re['pathid']:
                                if k['secl']:
                                    secl = True
                            nw.add_edge(node['node'], re['node'], pathid=pathid, secl=secl, engine=engine['engine'])
                        elif engine['role'] == 'border':
                            if re['node'] in pathid:
                                nw.add_edge(node['node'], re['node'], pathid=pathid, engine=engine['engine'])
                            else:
                                # ulgy hack
                                nw.add_edge(node['node'], re['node'], pathid=[0], secl=re['secl'],
                                            engine=engine['engine'])
                        else:
                            nw.add_edge(node['node'], re['node'], pathid=[], secl=re['secl'], engine=engine['engine'])
                if node['state'] == 'DEAD':
                    roles=['dead']
                roles.append((engine['engine'], engine['role']))
            if len(roles) == 0:
                roles = ['none']
            nx.set_node_attributes(nw, {node['node']: roles}, 'roles')
    return nw


def create_nw_color_list(nw):
    return ['tab:blue' if 'external' in i[0][1] else 'tab:brown' if 'border' in i[0][1] else 'tab:pink' if 'central' in i[0][1] else 'tab:grey' if 'dead' else 'tab:cyan'
            for i in nx.get_node_attributes(nw, 'roles').values()]

def create_nw_alpha_list(nw):
    return [1 if 'dead' not in i[0][1] else 0.5 for i in nx.get_node_attributes(nw, 'roles').values()]

def nw_axes(nw, ax):
    pos = nx.get_node_attributes(nw, 'pos')

    n_axes = nx.draw_networkx_nodes(nw, ax=ax, pos=pos, alpha=create_nw_alpha_list(nw), node_color=create_nw_color_list(nw))
    l_axes = nx.draw_networkx_labels(nw, ax=ax, pos=pos, font_size=9)
    e_alpha=1
    e_axes = nx.draw_networkx_edges(nw, ax=ax, pos=pos, alpha=e_alpha, connectionstyle="arc3,rad=0.2")
    return [n_axes] +list(l_axes.values()) + e_axes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='meas_4_plot_ff', description='Plot ', epilog=':-(')
    parser.add_argument('-f', '--file', dest='filename', help='Filename, use $1 for frame counter')
    parser.add_argument('-v', '--video', dest='video', action='store_true', help='Write video')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    parser.add_argument('-i', '--info', dest='info', action='store_true', default=False, help='Info mode')
    parser.add_argument('-n', '--network', dest='network', action='store_true', default=False, help='Plot also network')
    parser.add_argument('-p', '--per-frame', dest='per_frame', action='store_true', default=False, help='Per frame files')
    parser.add_argument('-c', '--count', dest='count', type=int, help='Count of frames')
    parser.add_argument('-s', '--static', dest='static', action='store_true', help='Generate still images')
    parser.add_argument('-r', '--resolution', dest='resolution', type=int, default=72, help='DPI')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    elif args.info:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    fig, ax = plt.subplots(nrows=1, ncols=1, layout='compressed', figsize=(15, 15))

    if args.per_frame:
        logger.info('Base filename: ' + str(args.filename))
        frames = []
        nw_frames = []
        artists = []
        for i in range(args.count):
            filename = args.filename.replace('$1', str(i))
            logger.info('Base filename: ' + str(filename))

            stream = open(filename, 'r')
            loader = yaml.safe_load(stream)

            frame = gen_frame(loader['plane']['plane'])
            frames.append(frame)
            artist = [ax.imshow(frame, animated=True, origin='lower', zorder=0)]
            if args.network:
                nw = construct_graph(loader['routing'])
                nw_frames.append(nw)
                nw_artist = nw_axes(nw, ax)
                artist += nw_artist
            artists.append(artist)
            if args.static:
                ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
                fig.savefig(filename + '.png', bbox_inches='tight', dpi=args.resolution)
        if args.static:
            exit(0)
    else:
        logger.info('Base filename: ' + str(args.filename))

        stream = open(args.filename, 'r')
        loader = yaml.safe_load(stream)

        frames = [gen_frame(i['plane']['plane']) for i in loader['nrg_list']]

        #x = np.arange(0, 100)
        #im, = ax.plot(x, x) # what does the , do?

        artists = [ax.imshow(frame, animated=True, origin='lower', zorder=0) for frame in frames]

        if args.network:
            nw_frames = [construct_graph(i['routing']) for i in loader['nrg_list']]
            nw_artists = [ nw_axes(nw,ax) for nw in nw_frames ]
            artists = [ nw_artist+[artist] for nw_artist, artist in zip(nw_artists, artists) ]

    ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
    ani = anm.ArtistAnimation(fig=fig, artists=artists, interval=400, repeat=True, blit=True, repeat_delay=1000)

    if args.video:
        ani.save("out.gif", dpi=args.resolution, writer=anm.PillowWriter(fps=2))
    else:
        plt.show()
