#!/bin/env python3

import numpy as np
import matplotlib.pyplot as plt


# Making a class circle and initializing it with its centre and radius
class circle:
    def __init__(self,radius,x,y):
        self.radius = radius
        self.x = x
        self.y = y

# Finding point that lies inside the circle
    def exist_in_circle(self, x1, y1):
        if (self.x-x1)*(self.x-x1)+(self.y-y1)*(self.y-y1) <= self.radius*self.radius:
            return True
        else:
            return False


def in_area(point):
    exist = [c.exist_in_circle(*point) for c in circles]
    return exist.count(True) > 0


# initializing plt of matplotlib
if __name__ == '__main__':
    fig, ax = plt.subplots()
    ax.set(xlim=(-1, 2), ylim=(-1, 2))

    x = np.linspace(0, 1, 100)
    y = np.linspace(0, 1, 100)
    xx, yy = np.meshgrid(x, y)
    print(x.shape, y.shape, xx.shape, yy.shape)
    #(100,)(100, )(100, 100)(100, 100)

    # initializing 3 circles as required in the question
    c1 = circle(1,1,0.5)
    c2 = circle(0.5,0.5,0.5)
    c3 = circle(0.4,0.1,0.1)

    circles = [c1, c2, c3]
    c = []
    for x, y in zip(np.ravel(xx), np.ravel(yy)):
        is_in_area = in_area((x, y))
        c.append(is_in_area)

    area = sum(c) / len(c)
    print(area)

    colors = list(map(lambda x: {True: 'b', False: 'w'}[x], c))
    plt.scatter(np.ravel(xx), np.ravel(yy), c=colors)
    plt.title(f'Area: {area}')


    # plotting circles and a square from (0,0) to (1,1)
    a_circle = plt.Circle((c1.x, c1.y), c1.radius, color='r', linewidth=1, fill=False)
    ax.add_artist(a_circle)
    a_circle = plt.Circle((c2.x, c2.y), c2.radius,color='b', linewidth=1, fill=False)
    ax.add_artist(a_circle)
    a_circle = plt.Circle((c3.x, c3.y), c3.radius,color='g', linewidth=1, fill=False)
    ax.add_artist(a_circle)
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color="k", linewidth=1, fill=False))

    # Printing the graph
    plt.show()
