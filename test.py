#!/usr/bin/env python

from gesture import Gesture, GestureDatabase

def main():
    g = Gesture()
    point_list = [(1,1), (3,4), (2,1)]
    g.add_stroke(point_list=point_list)
    g.normalize()

    gdb = GestureDatabase()
    gdb.add_gesture(g)

    new_point_list = [(x+1, y+1) for (x,y) in point_list]

    g2 = Gesture()
    g2.add_stroke(point_list=new_point_list)
    g2.normalize()
    print gdb.find(g2)

if __name__ == '__main__':
    main()