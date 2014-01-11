#!/usr/bin/env python

import sys
import subprocess
import json
import re
import signal
from time import time, sleep

lag_calculated = False


class PebbleReader:

    def __init__(self):
        self.proc = False
        signal.signal(signal.SIGINT, self.interrupt_handler)

    def read_from_pebble(self):
        self.proc = subprocess.Popen(
            ['unbuffer', 'pebble', 'logs'], stdout=subprocess.PIPE)
        self.print_input()
        # avg_lag = self.calculate_lag()
        # Average lag calculated running the above routine
        # avg_lag =  2.081870

        # self.out_file = open('data.txt', 'w')

    def calculate_lag(self):
        lag_times = []

        self.instruct('Lay your pebble flat on the table')
        self.wait_for_fuzzy_match(x=0, y=0, z=-50, frames_needed=5)

        for i in xrange(1,5):
            self.instruct_and_wait('Turn your Pebble on its left side, and immediately press Enter')
            self.get_lag_for_orientation(lag_times, x=-50)

            self.instruct_and_wait('Turn your Pebble on its right side, and immediately press Enter')
            self.get_lag_for_orientation(lag_times, x=50)

            self.instruct_and_wait('Turn your Pebble upside down (screen facing down), and immediately press Enter')
            self.get_lag_for_orientation(lag_times, z=50)

            self.instruct_and_wait('Turn your Pebble flat on the table (screen facing up), and immediately press Enter')
            self.get_lag_for_orientation(lag_times, z=-50)

        avg_lag = sum(lag_times) / float(len(lag_times))
        print 'Average Lag: %fs' % (avg_lag)
        return avg_lag

    def get_lag_for_orientation(self, lag_times, x=None, y=None, z=None):
        stopwatch = Stopwatch()
        self.wait_for_fuzzy_match(x=x, y=y, z=z)
        lag = stopwatch.get_time()
        print 'Lag of %fs' % lag
        lag_times.append(lag)

    def instruct_and_wait(self, str):
        self.instruct(str)
        self.wait_for_enter()

    def instruct(self, str):
        print '>>> %s' % str

    def wait_for_enter(self):
        raw_input("Press <Enter> to continue")

    def wait_for_fuzzy_match(self, x=None, y=None, z=None, tolerance=10, frames_needed=1):
        difference = tolerance + 1
        frame_count = 0

        while frame_count < frames_needed:
            while difference > tolerance:
                data = self.get_reading()
                difference = self.difference_from_target(x, y, z, data)
                if difference > tolerance:
                    print 'No match found -- Current Distance %d > %d (target)' % (difference, tolerance)
                    frame_count = 0
            frame_count += 1
            if frame_count < frames_needed:
                remaining_frames = frames_needed - frame_count
                print '%d frame%s remaining' % (remaining_frames, 's' if remaining_frames != 1 else '')
            else:
                print 'fuzzy match complete!'

    def print_input(self):
        while True:
            data = self.get_reading()
            print "%d, %d, %d" % (data['x0'], data['y0'], data['z0'])

    def difference_from_target(self, x, y, z, data):
        diff = 0
        if x:
            diff += pow(x - data['x'], 2)

        if y:
            diff += pow(y - data['y'], 2)

        if z:
            diff += pow(z - data['z'], 2)

        return diff

    def get_reading(self):
        line_regex = r'^\[INFO\s+\] JS: Happy Pebble: Received: ({.*})\n$'
        while True:
            line = self.proc.stdout.readline()
            if line != '':
                match = re.match(line_regex, line)
                if match:
                    json_text = match.group(1)
                    data = json.loads(json_text)
                    if data['cmd'] == 0:
                        return data
                else:
                    print '>%s' % line.rstrip()

    def write_line(self, data):
        line_to_write = "%s|%s|%s" % (data['x'], data['y'], data['z'])
        print '-->%s' % line_to_write
        self.out_file.write(line_to_write + '\n')
        self.out_file.flush()

    def on_exit(self):
        print '\nEnding Pebble process...'
        self.proc.send_signal(signal.SIGINT)
        self.proc.wait()
        print 'Pebble process terminated!'

    def close(self):
        self.on_exit()

    def interrupt_handler(self, signal_arg, frame):
        self.on_exit()
        sys.exit(0)

class Stopwatch:
    def __init__(self):
        self.start = time()

    def start(self):
        self.start = time()

    def get_time(self):
        return time() - self.start

def main():
    try:
        reader = PebbleReader()
        reader.read_from_pebble()
    except:
        raise
    finally:
        # No matter what happened, attempt to kill the child process so that the Pebble app frees up
        try:
            reader.close()
        except:
            pass


if __name__ == '__main__':
    main()
