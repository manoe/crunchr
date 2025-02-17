#!/bin/env python3

import matplotlib.animation as anm
import yaml
import numpy as np
import matplotlib.pyplot as plt
import argparse
import logging
logger = logging.getLogger(__name__)
import sys

from matplotlib import rcParams
rcParams['font.family'] = ['serif']
rcParams['font.serif'] = ['Times New Roman']

def map_value(value):
    if value == '1':
        return 0
    else:
        return 1

def gen_frame(plane):
    logger.debug('Array\'s shape (x,y): ' + str((len(plane), len(str(plane[0])))))
    frame = np.ndarray(shape=(len(plane), len(str(plane[0]))))
    for idx,i in enumerate(plane):
        frame[:,idx]=[map_value(j) for j in str(i['y'])]
    logger.debug(frame)
    return frame

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='meas_4_plot_ff', description='Plot ', epilog=':-(')
    parser.add_argument('-f','--file', dest='filename', help='Filename')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    logger.debug('Base filename: ' + str(args.filename))

    stream = open(args.filename, 'r')
    loader = yaml.safe_load(stream)

    fig, ax = plt.subplots()
    rng = np.random.default_rng(19680801)
    data = np.array([20, 20, 20, 20])
    x = np.array([1, 2, 3, 4])

    artists = []
    for i in loader:
        container = ax.imshow(gen_frame(i['plane']))
        artists.append(container)

    ani = anm.ArtistAnimation(fig=fig, artists=artists, interval=400)
    plt.show()
