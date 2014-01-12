#!/usr/bin/env python

import sys
import subprocess
import json
import re
import signal
import threading
from time import time

lag_calculated = False
NUM_READINGS_PER_COMM = 10


class PebbleReader:

    def __init__(self):
        self.proc = False
        signal.signal(signal.SIGINT, self.interrupt_handler)

    def read_from_pebble(self):
        self.proc = subprocess.Popen(
            ['unbuffer', 'pebble', 'logs'], stdout=subprocess.PIPE)
        # self.print_input()
        # self.avg_lag = self.calculate_lag()

        # Average lag calculated running the above routine
        self.avg_lag =  0.897269

        self.out_file = open('data.txt', 'w')

        self.train()

    def train(self):
        while True:
            self.train_with_result(1, 'positive')
            self.train_with_result(-1, 'negative')

    def train_with_result(self, score, label):
        while True:
            gesture = []
            end_time = -1

            c = self.instruct_and_get('Now training %s gestures. Press Enter then perform the %s gesture, or type any key before pressing Enter to end.' % (label, label))
            if c != '':
                return

            start_time = time() + self.avg_lag

            thread = ThreadedWait('Press Enter to stop performing the %s gesture' % label)
            thread.start()
            while end_time == -1 or time() < end_time:
                if end_time == -1 and not thread.is_alive():
                    print 'Please wait...'
                    end_time = time() + self.avg_lag

                data = self.get_reading()
                if time() <= start_time:
                    for reading_idx in xrange(NUM_READINGS_PER_COMM):
                        r_str = str(reading_idx)
                        gesture.append((data['x' + r_str], data['y' + r_str], data['z' + r_str]))
            self.write_gesture(gesture, score)

    def write_gesture(self, gesture, score):
        # Normalize each gesture
        out_line = str(score)
        for point in gesture:
            out_line += '|' + str(point[0]) + ',' + str(point[1]) + ',' + str(point[2])

        self.out_file.write(out_line + '\n')
        self.out_file.flush()




    def calculate_lag(self):
        lag_times = []

        self.instruct('Lay your pebble flat on the table')
        self.wait_for_fuzzy_match(x=0, y=0, z=-1000, frames_needed=5)

        for i in xrange(1,5):
            self.instruct_and_wait('Turn your Pebble on its left side, and immediately press Enter')
            self.get_lag_for_orientation(lag_times, x=-1000)

            self.instruct_and_wait('Turn your Pebble on its right side, and immediately press Enter')
            # Higher tolerance here because of the buttons
            self.get_lag_for_orientation(lag_times, x=1000, tolerance=1000)

            self.instruct_and_wait('Turn your Pebble upside down (screen facing down), and immediately press Enter')
            self.get_lag_for_orientation(lag_times, z=1000)

            self.instruct_and_wait('Turn your Pebble flat on the table (screen facing up), and immediately press Enter')
            self.get_lag_for_orientation(lag_times, z=-1000)

        avg_lag = sum(lag_times) / float(len(lag_times))
        print 'Average Lag: %fs' % (avg_lag)
        return avg_lag

    def get_lag_for_orientation(self, lag_times, x=None, y=None, z=None, tolerance=500):
        stopwatch = Stopwatch()
        self.wait_for_fuzzy_match(x=x, y=y, z=z, tolerance=tolerance)
        lag = stopwatch.get_time()
        print 'Lag of %fs' % lag
        lag_times.append(lag)

    def instruct_and_get(self, str):
        return raw_input('>>> %s' % str)

    def instruct_and_wait(self, str):
        self.instruct(str)
        self.wait_for_enter()

    def instruct(self, str):
        print '>>> %s' % str

    def wait_for_enter(self):
        raw_input("Press <Enter> to continue ")

    def wait_for_fuzzy_match(self, x=None, y=None, z=None, tolerance=500, frames_needed=1):
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
            print "%d, %d, %d" % (data['x'], data['y'], data['z'])

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
                        data['x'] = data['y'] = data['z'] = 0
                        for key in data:
                            if key == 'cmd' or key == 'x' or key == 'y' or key == 'z':
                                continue

                            if key[0] == 'x':
                                data['x'] += data[key]
                            elif key[0] == 'y':
                                data['y'] += data[key]
                            else:
                                data['z'] += data[key]

                        data['x'] /= NUM_READINGS_PER_COMM
                        data['y'] /= NUM_READINGS_PER_COMM
                        data['z'] /= NUM_READINGS_PER_COMM
                        return data
                else:
                    print '>%s' % line.rstrip()

    def write_line(self, data):
        line_to_write = "%s|%s|%s" % (data['x'], data['y'], data['z'])
        print '-->%s' % line_to_write
        self.out_file.write(line_to_write + '\n')
        self.out_file.flush()

    def on_exit(self):
        if self.out_file:
            print 'Closing output file...'
            self.out_file.close()
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

class ThreadedWait(threading.Thread):
    def __init__(self, prompt):
        threading.Thread.__init__(self)
        self.prompt = prompt

    def run(self):
        self.input = raw_input(self.prompt)

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
        except OSError:
            sys.exit(0)
            pass


if __name__ == '__main__':
    main()
