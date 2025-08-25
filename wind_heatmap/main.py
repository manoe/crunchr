#!/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import logging
logger = logging.getLogger(__name__)
import sys

from matplotlib import rcParams
rcParams['font.family'] = ['serif']
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 18

def f_w_a(angle, c_w_a=0.3):
    if not c_w_a < 1.0:
        raise Exception('c_w_a must be > 1.0')

    return c_w_a * np.sign(np.cos(angle)) * np.pow(np.cos(angle),2)

def f_w_s(speed, c_w_s=1.0, c_w_l=0.0, c_w_m=1.0):
    return c_w_s * sigmoid((12.0 + c_w_l)/c_w_m * speed - 6 - c_w_l)

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logger.info('Loading data')
    angle_arr = np.linspace(0, 2 * np.pi, 100)
    speed_arr = np.linspace(0, 1, 100)

    angle_tick_arr = np.linspace(0, 2 * np.pi, 10)
    speed_tick_arr = np.linspace(0, 1, 10)

    value_map = np.ndarray(shape=(len(angle_arr), len(speed_arr)))
    for idx_angle, angle in enumerate(angle_arr):
        for idx_speed, speed in enumerate(speed_arr):
            value_map[idx_angle, idx_speed] = 1/(1 - f_w_a(angle) * f_w_s(speed))

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(9, 7.5))

    ax = plt.subplot(1,1,1)
    im = ax.imshow(value_map, origin='lower')
    fig.subplots_adjust(left=-0.05, right=1.1)
    cax = cbar_ax = fig.add_axes([0.9, 0.11, 0.04, 0.775])
    fig.colorbar(im,cax=cax, label='Sensing adjustment coefficient')

    ax.set_yticks(np.arange(0, len(angle_arr), len(angle_arr)/10))
    ax.set_xticks(np.arange(0, len(speed_arr), len(angle_arr)/10))
    ax.set_yticklabels([ '{:,.2f}'.format(i) for i in np.linspace(0, 2 * np.pi, 1+len(ax.get_yticks()))][:-1])
    ax.set_xticklabels([ '{:,.2f}'.format(i) for i in np.linspace(0, 1, 1+len(ax.get_xticks()))][:-1])
    ax.set_ylabel('Wind angle')
    ax.set_xlabel('Wind speed')
#    plt.tight_layout()
    plt.savefig('out.pdf', bbox_inches='tight')

    plt.show()
