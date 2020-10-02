import argparse
import json
from pathlib import Path


ignore_keys = ['_id', 'delay', 'label']


def find_distribution(windows):
    devices = [key for key in windows[0].keys() if key not in ignore_keys]
    dist_dict = {str(num): {'len': 0, 'windows': []} for num in range(1, 8)}

    ddos_threshold = 1_000
    for window in windows:
        num_attackers = 0
        for dev in devices:
            if window[dev]['outgoing'] > ddos_threshold:
                num_attackers += 1
        dist_dict[str(num_attackers)]['len'] += 1
        dist_dict[str(num_attackers)]['windows'].append(window)

    return dist_dict


def gen_heatmaps(val, out_dir):
    # TODO implement this
    pass


def main(fin, write_dir, label):
    traffic_windows = []
    try:
        with open(fin) as file:
            for jsonObj in file:
                window = json.loads(jsonObj)
                traffic_windows.append(window)
    except FileNotFoundError:
        print(f'Unable to find file {fin}')

    dist_dict = find_distribution(traffic_windows)
    out_dir = Path(write_dir)
    for val in dist_dict.values():
        gen_heatmaps(val, out_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create a heatmap dataset from a json mongoexport file')
    parser.add_argument('in_file', type=str,
                        help='mongoexport file to read from')
    parser.add_argument('dir', type=str, help='destination folder to write to')
    parser.add_argument(
        'label', type=str,
        help='classification of in_file contents eg. ddos, norm')
    args = parser.parse_args()
    main(args.in_file, args.dir, args.label)
