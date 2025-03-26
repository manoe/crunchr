import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.family'] = ['serif']
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 20
from matplotlib import ticker

if __name__ == '__main__':
    x = [2, 5, 4]
    y = [0.125, 0.5, 0.75]
    label = ['a', 'b', 'c']
    fig,axs = plt.subplots(1,1,layout='constrained')
    axs.scatter(x, y)
    for idx, i in enumerate(label):
        axs.annotate(i, xy=(x[idx], y[idx]))
    axs.set_ylim([0, 1.])
    axs.set_xlabel('Hop')
    axs.set_ylabel('Energy')
    axs.set_xlim([0,6])
    axs.grid()
    #plt.
    plt.savefig('topsis.pdf')
    plt.show()
