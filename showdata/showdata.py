
import json
import argparse
import re
import matplotlib.pyplot as plt

def draw_defined_speed(defined_file):
    with open(defined_file, 'r') as f:
        data = json.load(f)
    t = []
    s = []
    for event in data['events']:
        if s:
            t.append(event['time'])
            s.append((s[len(s)-1]))
        t.append(event['time'])
        if event['params'].has_key('bw'):
            s.append(event['params']['bw'] * 1024)
        else:
            s.append(0)
    # print t
    # print s
    # plt.xlabel('time(seconds)')
    # plt.ylabel('realtime speed(Kbps)')
    # plt.plot(t, s, 'b')
    # plt.show()
    return t, s

def draw_realtime_speed(realtime_file):
    with open(realtime_file, 'r') as f:
        lines = f.readlines()
    t = []
    s = []
    for line in lines:
        result = re.search(r'(\d*), (\d*\.?\d*)', line)
        t.append(int(result.group(1)))
        s.append(float(result.group(2)))
    # print t
    # print s
    # plt.xlabel('time(seconds)')
    # plt.ylabel('realtime speed(Kbps)')
    # plt.plot(t, s, 'b')
    # plt.show()
    return t, s

def draw_output(output_file, *args):
    plt.xlabel('time(seconds)')
    plt.ylabel('realtime speed(Kbps)')
    print args[0]
    print args[1]
    plt.plot(args[0], args[1], label='defined_speed', color='r')
    plt.plot(args[2], args[3], label='realtime_speed', color='b')
    plt.legend(loc='upper right')
    # plt.show()
    plt.savefig(output_file)


if __name__ == '__main__':
    print "ad"
    parser = argparse.ArgumentParser()
    parser.add_argument("--defined", default="../dash_minievents.json", help="input defined speed txt")
    parser.add_argument("--realtime", default="../speed_output/speed_test.txt", help="input realtime speed txt")
    parser.add_argument("--output", default="./output.png", help="output image")
    args = parser.parse_args()

    t1, s1 = draw_defined_speed(args.defined)
    t2, s2 = draw_realtime_speed(args.realtime)
    draw_output(args.output, t1, s1, t2, s2)