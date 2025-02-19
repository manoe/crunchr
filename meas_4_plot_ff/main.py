#!/bin/env python3
import matplotlib.animation as anm
import yaml
import numpy as np
import matplotlib.pyplot as plt
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
    NO_FUEL     = 0
    NOT_IGNITED = 1
    BURNING     = 2
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
    logger.debug('Array\'s shape (x,y): ' + str((len(plane), len(str(plane[0]['y'])))))
    frame = np.ndarray(shape=(len(plane), len(str(plane[0]['y'])),4), dtype=np.uint8)
    for idx, i in enumerate(plane):
        logger.debug('Array\'s idx: ' + str(idx))
        frame[:, idx,:] = [map_value(j) for j in str(i['y'])]
    logger.debug(frame)
    return np.flipud(frame)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='meas_4_plot_ff', description='Plot ', epilog=':-(')
    parser.add_argument('-f', '--file', dest='filename', help='Filename')
    parser.add_argument('-v','--video', dest='video', action='store_true', help='Write video')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    logger.debug('Base filename: ' + str(args.filename))

    stream = open(args.filename, 'r')
    loader = yaml.safe_load(stream)

    fig, ax = plt.subplots(nrows=1, ncols=1, layout='compressed')

    frames = [gen_frame(i['plane']) for i in loader]
    artists = [ [ax.imshow(frame, animated=True)] for frame in frames]
    ani = anm.ArtistAnimation(fig=fig, artists=artists, interval=400, repeat=True, blit=True, repeat_delay = 1000)

    if args.video:
        ani.save("out.gif", dpi=300, writer=anm.PillowWriter(fps=2))
    else:
        plt.show()
