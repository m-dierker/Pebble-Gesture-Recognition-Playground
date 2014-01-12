from math import sqrt, pow
import matplotlib.pyplot as plt
import copy
import numpy as np

class Gesture:
    def __init__(self):
        self.points = []

    def add_point(self, x, y):
        self.points.append(Point(x,y))

    def length(self):
        length = 0
        for i in xrange(len(self.points) - 1):
            length += self.points[i].distance_to(self.points[i+1])
        return length

    def normalize(self, sample_points=5):
        total_length = self.length()
        seg_length = total_length / float(sample_points - 1)

        new_points = []

        start = self.points[0]
        new_points.append(start)

        rem_dist = seg_length

        for curr in self.points[1:]:
            if curr == self.points[len(self.points)-1]:
                print curr
                print start.distance_to(curr)
                print rem_dist

            should_repeat = True
            while should_repeat:
                should_repeat = False
                dist = start.distance_to(curr)

                # rem_dist > dist
                if rem_dist > dist:
                    start = curr
                    rem_dist -= dist
                    break

                ratio = rem_dist / dist
                new_x = start.x + ratio * (curr.x - start.x)
                new_y = start.y + ratio * (curr.y - start.y)
                new_point = Point(new_x, new_y)
                new_points.append(new_point)

                rem_dist = seg_length
                start = new_point
                should_repeat = True

        if len(new_points) == sample_points - 1:
            new_points.append(copy.deepcopy(self.points[len(self.points) - 1]))

        assert len(new_points) == sample_points

        nums = np.array([point.tuple() for point in new_points])
        nums = nums - nums.mean(axis=0)
        nums = nums / nums.std(axis=0)
        nums = np.around(nums, 9)

        new_points = []
        for coords in nums.tolist():
            new_points.append(Point(coords[0], coords[1]))

        self.points = new_points

        # new_x = [point.x for point in new_points]
        # new_y = [point.y for point in new_points]

        # orig_x = [point.x for point in self.points]
        # orig_y = [point.y for point in self.points]

        # fig = plt.figure()
        # ax = fig.add_subplot(111)
        # ax.plot(orig_x, orig_y, 'bo-')
        # ax.plot(new_x, new_y, 'ro-')
        # plt.show()




class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return '(%s,%s)' % (self.x, self.y)

    def tuple(self):
        return (self.x, self.y)

    def distance_to(self, dest):
        return sqrt(pow(self.x - dest.x, 2) + pow(self.y - dest.y, 2))