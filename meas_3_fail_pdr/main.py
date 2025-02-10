#!/bin/env python3

import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import datetime


2 1 97 0.3389830508474576
2 2 64 0.3737864077669903
2 3 47 0.0995850622406639
2 4 18 0.15163934426229508
2 5 2 0.0
28 1 99 0.8951612903225806
28 2 84 0.48627450980392156
28 3 71 0.0
28 4 72 0.0
28 5 28 0.0
21 1 82 0.9292035398230089
21 2 98 0.0
21 3 52 1.6140350877192982
21 4 21 0.0


if __name__ == '__main__':
    x = [
        datetime.datetime(2011, 1, 4, 0, 0),
        datetime.datetime(2011, 1, 5, 0, 0),
        datetime.datetime(2011, 1, 6, 0, 0)
    ]
    x = date2num(x)

    level_1 = [0.3389830508474576, 0.3737864077669903, 0.0995850622406639]
    level_2 = [0.8951612903225806, 0.48627450980392156, 0.0]

    y = [4, 9, 2]
    z = [1, 2, 3]
    k = [11, 12, 13]

    ax = plt.subplot(111)
    ax.bar(x-0.2, y, width=0.2, color='b', align='center')
    ax.bar(x, z, width=0.2, color='g', align='center')
    ax.bar(x+0.2, k, width=0.2, color='r', align='center')
    ax.xaxis_date()

    plt.show()