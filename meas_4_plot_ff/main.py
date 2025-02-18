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

class CellState(Enum):
    NO_FUEL     = 0
    NOT_IGNITED = 1
    BURNING     = 2
    BURNED_DOWN = 3

def map_value(value):
    if value == '1':
        return 0.0
    else:
        return 1.0


def gen_frame(plane):
    logger.debug('Array\'s shape (x,y): ' + str((len(plane), len(str(plane[0]['y'])))))
    frame = np.ndarray(shape=(len(plane), len(str(plane[0]['y']))))
    for idx, i in enumerate(plane):
        logger.debug('Array\'s idx: ' + str(idx))
        frame[:, idx] = [map_value(j) for j in str(i['y'])]
    logger.debug(frame)
    return frame


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='meas_4_plot_ff', description='Plot ', epilog=':-(')
    parser.add_argument('-f', '--file', dest='filename', help='Filename')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    logger.debug('Base filename: ' + str(args.filename))

    stream = open(args.filename, 'r')
    loader = yaml.safe_load(stream)

    fig, ax = plt.subplots(nrows=1, ncols=1)
    frames = [gen_frame(i['plane']) for i in loader]
    artists = [ [ax.imshow(frame, animated=True)] for frame in frames]
    ani = anm.ArtistAnimation(fig=fig, artists=artists, interval=400, repeat=True, blit=True, repeat_delay = 1000)

    plt.show()
