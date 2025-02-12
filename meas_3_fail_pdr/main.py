#!/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
rcParams['font.family'] = ['serif']
rcParams['font.serif'] = ['Times New Roman']

#                                                             0.14059196617336153 0.213160664
# 31                  1                   97                  0.0                 0.243262157
# 31                  2                   96                  0.11316648531011969 0.208960444
# 31                  3                   81                  0.08990011098779134 0.194259718
# 31                  4                   65                  0.2139588100686499  0.229261458
# 31                  5                   47                  0.23076923076923078 0.219810992

#                                                             0.27364185110663986 0.213160664
# 26                  1                   82                  0.0                 0.182709143
# 26                  2                   53                  0.0                 0.175358772
# 26                  3                   55                  0.19333333333333333 0.196359813
# 26                  4                   40                  0.2813186813186813  0.20546028
# 26                  5                   25                  0.26406926406926406 0.193209663

#                                                             0.23162583518930957 0.213160664
# 43                  1                   94                  0.1762208067940552  0.201960102
# 43                  2                   95                  0.06904231625835189 0.152257606
# 43                  3                   98                  0.06136363636363636 0.206160307
# 43                  4                   84                  0.24764150943396226 0.225761294
# 43                  5                   71                  0.07126436781609195 0.192159608

#                                                             0.29535864978902954 0.213160664
# 20                  1                   110                 0.354978354978355   0.198459923
# 20                  2                   95                  0.0                 0.152257606
# 20                  3                   51                  0.27391304347826084 0.194609731
# 20                  4                   20                  0.0                 0.159257963

#                                                             0.1955193482688391  0.213160664
# 24                  1                   98                  0.0                 0.206160307
# 24                  2                   68                  0.14485981308411214 0.184109211
# 24                  3                   54                  0.09513274336283185 0.186909348
# 24                  4                   24                  0.0                 0.160308018


if __name__ == '__main__':
    x = np.arange(0, 4)

    path_0 = [0.14059196617336153, 0.0,                0.11316648531011969, 0.08990011098779134]
    path_1 = [0.27364185110663986, 0.0,                0.0,                 0.19333333333333333]
    path_3 = [0.23162583518930957, 0.1762208067940552, 0.06904231625835189, 0.06136363636363636]
    path_4 = [0.29535864978902954, 0.354978354978355,  0.0,                 0.27391304347826084]
    path_5 = [0.1955193482688391,   0.0,                0.14485981308411214, 0.09513274336283185]

    paths = [path_0, path_1, path_3, path_4, path_5]

    e2e_pdr_0 =[ 0.213160664, 0.243262157, 0.208960444, 0.194259718 ]
    e2e_pdr_1 =[ 0.213160664, 0.182709143, 0.175358772, 0.196359813]
    e2e_pdr_2 =[ 0.213160664, 0.201960102, 0.152257606, 0.206160307]
    e2e_pdr_3 =[ 0.213160664, 0.198459923, 0.152257606, 0.194609731]
    e2e_pdr_4 =[ 0.213160664, 0.206160307, 0.184109211, 0.186909348]

    e2e_pdrs = [e2e_pdr_0, e2e_pdr_1, e2e_pdr_2, e2e_pdr_3, e2e_pdr_4]

    fig, axs = plt.subplots(nrows=2, ncols=1, constrained_layout=True)
    width = 1.0/len(paths)
    ax=axs[0]
    for idx, path in enumerate(paths):
        ax.bar(x+width*idx*0.6-0.25, path, width=width*0.5, align='center')
    ax.set_xticks(x)
    ax.set_title('(a)', loc='left', x=-0.09, pad=15) # axs.set_title(title[idx], loc='left', pad=5, x=-0.07)
    ax.set_xticklabels(['No failure', r'1$^\mathregular{st}$ hop failre', r'2$^\mathregular{nd}$ hop failure', r'3$^\mathregular{rd}$ hop failure'])
    path_labels = ['Path '+str(idx+1) for idx in range(len(paths)) ]
    ax.legend(path_labels, loc='upper right', ncols=3)
    ax.grid(True, axis='y')
    #ax.set_xlabel('Failing node\'s level')
    ax.set_ylabel('Path level PDR')

    ax=axs[1]
    for idx, e2e_pdr in enumerate(e2e_pdrs):
        ax.bar(x+width*idx*0.6-0.25, e2e_pdr, width=width*0.5, align='center')

    ax.set_title('(b)', loc='left', x=-0.09, pad=15)
    ax.set_ylabel('End-to-end PDR')
    ax.set_xticks(x)
    ax.set_xticklabels(['No failure', r'1$^\mathregular{st}$ hop failre', r'2$^\mathregular{nd}$ hop failure',
                        r'3$^\mathregular{rd}$ hop failure'])
    ax.grid(True, axis='y')
    plt.show()
    plt.savefig('single_node_fail_path.pdf')