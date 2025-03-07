#!/bin/env python3
import matplotlib.animation as anm
import yaml
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx
import argparse
import logging
import pandas as pd
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

def map_pkt_value(value):
    logger.debug(int(value))
    if value > 0:
        return mcolors.to_rgb(mcolors.TABLEAU_COLORS['tab:green'])
    if value == 0:
        return mcolors.to_rgb(mcolors.BASE_COLORS['w'])
    else:
        return mcolors.to_rgb(mcolors.TABLEAU_COLORS['tab:gray'])

def map_mob_value(value):
    logger.debug(int(value))
    if value:
        return mcolors.to_rgb(mcolors.TABLEAU_COLORS['tab:brown'])
    else:
        return mcolors.to_rgb(mcolors.BASE_COLORS['w'])

def custom_to_numpy(dframe):
    frame = np.ndarray(shape=(len(dframe.index), len(dframe.columns), 3), dtype=float)
    for i, index in enumerate(dframe.index):
        for j, column in enumerate(dframe.columns):
            frame[i][j] = map_pkt_value(dframe[column][index])
    return frame

def mob_custom_to_numpy(dframe):
    frame = np.ndarray(shape=(len(dframe.index), len(dframe.columns), 3), dtype=float)
    for i, index in enumerate(dframe.index):
        for j, column in enumerate(dframe.columns):
            frame[i][j] = map_mob_value(dframe[column][index])
    return frame

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

def get_attribute_list(pkt_list, attribute):
    res = pd.Series()
    for i in pkt_list:
        if i['role'] != 'central':
            res.at[i['node']] = i[attribute]
    return res

def gen_diff(table):
    res = pd.DataFrame(index=table.index, columns=table.columns[1:])

    for i in table.index:
        row = list(table.loc[i])
        res.loc[i] = [b-a for a,b in zip(row[:-1], row[1:])]
    return res

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
    parser.add_argument('-m', '--messages', dest='messages', action='store_true', default=False, help='Show message arrivals')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    elif args.info:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    fig, (ax_nw, ax_pkt, ax_mob) = plt.subplots(nrows=3, ncols=1, layout='compressed', figsize=(15, 25), height_ratios = [15, 5, 5])


    if args.per_frame:
        logger.info('Base filename: ' + str(args.filename))
        frames = []
        nw_frames = []
        artists = []
        timestamps = []

        if args.messages:
            filename = args.filename.replace('$1', str(0))
            logger.info('Init filename: ' + str(filename))
            stream = open(filename, 'r')
            loader = yaml.safe_load(stream)
            pkt_frame = pd.DataFrame(index=[i['node'] for i in loader['nodes'] if i['role'] != 'central'],
                                 columns=[i for i in np.arange(-1,args.count)], data=0)
            pkt_frames = [pkt_frame]
            mobility_frame = pd.DataFrame(index=[i['node'] for i in loader['nodes'] if i['role'] != 'central'],
                                 columns=[i for i in np.arange(0,args.count)], data=False)

            state_frame = pd.DataFrame(data=pkt_frame)

        for i in range(args.count):
            filename = args.filename.replace('$1', str(i))
            logger.info('Actual filename: ' + str(filename))

            stream = open(filename, 'r')
            loader = yaml.safe_load(stream)
            timestamp = loader['timestamp']
            timestamps.append(timestamp)
            frame = gen_frame(loader['plane']['plane'])
            frames.append(frame)
            artist = [ax_nw.imshow(frame, animated=True, origin='lower', zorder=0)]

            if args.network:
                nw = construct_graph(loader['routing'])
                nw_frames.append(nw)
                nw_artist = nw_axes(nw, ax_nw)
                artist += nw_artist

            if args.messages:
                pkt_frame = pd.DataFrame(data=pkt_frames[-1])
                pkt_frame[i]=get_attribute_list(loader['nodes'], 'report_recv')
                state_frame[i]=get_attribute_list(loader['nodes'], 'state')
                mobility_frame[i]=get_attribute_list(loader['nodes'], 'mobility')

                pkt_frames.append(pkt_frame)
                dframe = gen_diff(pkt_frame)
                if i < args.count - 1:
                    dframe[i+1] = 0

                for k in dframe.index:
                    for j in dframe.columns:
                        if state_frame[j][k] == 'dead':
                            dframe[j][k] = -1
                image = custom_to_numpy(dframe)

                mob_image = mob_custom_to_numpy(mobility_frame)

                mob_tup = [(tuple(x)[0], tuple(x)[1]) for x in mobility_frame.stack().reset_index().values.tolist() if x[2] == True]
                artist.append(ax_pkt.imshow(image, origin='lower', animated=True, aspect='auto', interpolation='none'))
                artist.append(ax_pkt.scatter([x[1] for x in mob_tup ], [x[0] for x in mob_tup], color='red', marker='X'))

                artist.append(ax_mob.imshow(mob_image, origin='lower', aspect='auto', interpolation='none'))

            title = ax_nw.text(1, 1.01, "Timestamp: {:.2f}".format(timestamp),
                            size=plt.rcParams["axes.titlesize"],
                            ha="right", transform=ax_nw.transAxes )
            artist.append(title)
            artists.append(artist)
            if args.static:
                ax_nw.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
                fig.savefig(filename + '.png', bbox_inches='tight', dpi=args.resolution)
        if args.static:
            exit(0)
        ax_nw.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
    else:
        logger.info('Base filename: ' + str(args.filename))

        stream = open(args.filename, 'r')
        loader = yaml.safe_load(stream)

        frames = [gen_frame(i['plane']['plane']) for i in loader['nrg_list']]
        timestamps = [i['timestamp'] for i in loader['nrg_list']]

        #x = np.arange(0, 100)
        #im, = ax.plot(x, x) # what does the , do?

        artists = [ax_nw.imshow(frame, animated=True, origin='lower', zorder=0) for frame in frames]

        if args.network:
            nw_frames = [construct_graph(i['routing']) for i in loader['nrg_list']]
            nw_artists = [ nw_axes(nw,ax_nw) for nw in nw_frames ]

            artists = [ nw_artist+[artist] for nw_artist, artist in zip(nw_artists, artists) ]

        ax_nw.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
    ani = anm.ArtistAnimation(fig=fig, artists=artists, interval=400, repeat=True, blit=True, repeat_delay=1000)

    if args.video:
        ani.save("out.gif", dpi=args.resolution, writer=anm.PillowWriter(fps=3))
    else:
        plt.show()
