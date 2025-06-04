#!/bin/env python3

import numpy as np
import logging
logger = logging.getLogger(__name__)
from enum import IntEnum
import argparse
import yaml
import sys


def gen_frame(plane):
    logger.debug('Array\'s shape (y,x): ' + str((len(plane), len(str(plane[0]['y'])))))
    frame = np.ndarray(shape=(len(plane), len(str(plane[0]['y']))), dtype=CellState)
    for idx, i in enumerate(plane):
        logger.debug('Array\'s idx: ' + str(idx))
        frame[idx, :] = [CellState(int(j)) for j in str(i['y'])]
    logger.debug(frame)
    return frame

class CellState(IntEnum):
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='calc_burnt_area', description='Plot ', epilog=':-(')
    parser.add_argument('-f', '--file', dest='filename', help='Filename, use $1 for frame counter')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    parser.add_argument('-i', '--info', dest='info', action='store_true', default=False, help='Info mode')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    elif args.info:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    stream = open(args.filename, 'r')
    loader = yaml.safe_load(stream)
    frame = gen_frame(loader['plane']['plane'])

    unique, counts = np.unique(frame, return_counts=True)
    res = dict(zip(unique, counts))

    print('Not ignited ratio: '+str(res[CellState.NOT_IGNITED]/sum(counts)))