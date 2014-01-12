#!/usr/bin/eny python

import signal
from pointgesture import Gesture
import re
import sys

class Formatter:
    def __init__(self, in_file_name, out_file_name):
            self.in_file = open(in_file_name, 'r')
            self.out_file = open(out_file_name, 'w')
            signal.signal(signal.SIGINT, self.interrupt_handler)
            self.format_data()

    def format_data(self):
        for line in self.in_file:
            match = re.match(r'^(\-?1)((?:\|\-?\d+,\-?\d+)*)$', line)
            result = match.group(1)
            coord_str = match.group(2)

            points = re.findall(r'\|(\-?\d+),(\-?\d+)', coord_str)
            print points

            g = Gesture()

            for point in points:
                g.add_point(float(point[0]), float(point[1]))

            g.normalize()

            result_str = '+1' if result == '1' else '-1'
            out_line = result_str
            feature_count = 1

            for point in g.points:
                out_line += ' %d:%s' % (feature_count, point.x)
                feature_count += 1

                out_line += ' %d:%s' % (feature_count, point.y)
                feature_count += 1
            out_line += '\n'
            self.out_file.write(out_line)


    def close(self):
        if self.in_file:
            self.in_file.close()

        if self.out_file:
            self.out_file.close()

    def interrupt_handler(self, signal_arg, frame):
        self.close()
        sys.exit(0)


if __name__ == '__main__':
    formatter = Formatter('2ddata.txt', '2dformatted-data.txt')
    formatter.close()