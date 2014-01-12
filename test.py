#!/usr/bin/env python

from gesture import Gesture, GestureDatabase
from matplotlib.pyplot import plot
import matplotlib.pyplot as pyp

def main():
    g = Gesture()
    point_list = [(0,0), (1,0), (1,1), (0,1), (0,2), (2,2), (4,2), (5,3), (4,3), (3,3), (0,3), (1,2), (2,3), (4,5), (2,4), (1,4)]
    point_list.extend([(point[0]+1, point[1]+2) for point in point_list])
    point_list.extend([(point[0]+10, point[1]+20) for point in point_list])
    print len(point_list)
    g.add_stroke(point_list=point_list)
    g.normalize()

    points = g.strokes[0].points
    x = [point.x for point in points]
    y = [point.y for point in points]

    plot(x,y, 'bo-')
    pyp.show()

    # gdb = GestureDatabase()
    # gdb.add_gesture(g)

    # new_point_list = [(x+1, y+1) for (x,y) in point_list]

    # g2 = Gesture()
    # g2.add_stroke(point_list=new_point_list)
    # g2.normalize()
    # print gdb.find(g2)

if __name__ == '__main__':
    main()