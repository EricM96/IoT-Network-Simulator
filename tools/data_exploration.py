#!/usr/bin/python3
from pprint import pprint
import sys
import json


ignore_keys = ['_id', 'delay', 'label']


def find_max_packets(windows, mode):
    devices = [key for key in windows[0].keys() if key not in ignore_keys]
    host, cur_max = '', 0
    for window in windows:
        for dev in devices:
            if (outgoing := window[dev][mode]) > cur_max:
                host, cur_max = dev, outgoing
    return host, cur_max


def find_avg_packets(windows, mode):
    devices = [key for key in windows[0].keys() if key not in ignore_keys]
    sum_pkts = 0
    for window in windows:
        for dev in devices:
            sum_pkts += window[dev][mode]
    return sum_pkts / (len(windows) * len(devices))


def find_avg_dict(windows, mode):
    devices = [key for key in windows[0].keys() if key not in ignore_keys]
    avg_dict = {}
    for dev in devices:
        avg_dict[dev] = 0
    for window in windows:
        for dev in devices:
            avg_dict[dev] += window[dev][mode]
    for dev in devices:
        avg_dict[dev] /= len(windows)
    return avg_dict


def find_distribution(windows):
    devices = [key for key in windows[0].keys() if key not in ignore_keys]
    dist_dict = {}

    ddos_threshold = 1_000
    for window in windows:
        num_attackers = 0
        for dev in devices:
            if window[dev]['outgoing'] > ddos_threshold:
                num_attackers += 1
        if str(num_attackers) not in dist_dict.keys():
            dist_dict[str(num_attackers)] = 1
        else:
            dist_dict[str(num_attackers)] += 1

    return dist_dict


def main():
    if len(sys.argv) != 2:
        print('Usage: data_exploration.py <file_name>')
        sys.exit()
    file_name = sys.argv[1]

    traffic_windows = []
    try:
        with open(file_name) as fin:
            for jsonObj in fin:
                window = json.loads(jsonObj)
                traffic_windows.append(window)
    except FileNotFoundError:
        print(f'Unable to find file {file_name}')

    dist = find_distribution(traffic_windows)
    host, max_outgoing = find_max_packets(traffic_windows, 'outgoing')
    host, max_incoming = find_max_packets(traffic_windows, 'incoming')
    avg_sent = find_avg_packets(traffic_windows, 'outgoing')
    avg_recv = find_avg_packets(traffic_windows, 'incoming')
    avg_dict_sent = find_avg_dict(traffic_windows, 'outgoing')
    avg_dict_recv = find_avg_dict(traffic_windows, 'incoming')
    pprint(dist)
    print(f'Max egressing packets: {host} {max_outgoing}')
    print(f'Max ingressing packets: {max_incoming}')
    print(f'Average packets sent all: {avg_sent}')
    print(f'Average packets received all: {avg_recv}')
    print('Average packets sent per:')
    pprint(avg_dict_sent)
    print('Average packets received all:')
    pprint(avg_dict_recv)


if __name__ == '__main__':
    main()
