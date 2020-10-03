import argparse
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


ignore_keys = ['_id', 'delay', 'label']


def find_distribution(windows):
    devices = [key for key in windows[0].keys() if key not in ignore_keys]
    dist_dict = {str(num): {'len': 0, 'windows': []} for num in range(0, 8)}

    ddos_threshold = 1_000
    for window in windows:
        num_attackers = 0
        for dev in devices:
            if window[dev]['outgoing'] > ddos_threshold:
                num_attackers += 1
        dist_dict[str(num_attackers)]['len'] += 1
        dist_dict[str(num_attackers)]['windows'].append(window)

    return dist_dict


def write_heatmap(window, target, vmin, vmax):
    for key in ignore_keys:
        del window[key]

    traffic_window = pd.DataFrame.from_dict(
        window, orient='index')

    max_val = vmax + (vmax - vmin)
    plt.tight_layout()
    _ = sns.heatmap(traffic_window, xticklabels=False,
                    yticklabels=False, cbar=False, vmin=vmin, vmax=max_val)
    plt.ylabel('')
    plt.xlabel('')
    plt.savefig(target / ('sample' + str(write_heatmap.counter) + '.png'),
                format='png')
    write_heatmap.counter += 1


write_heatmap.counter = 0


def gen_heatmaps(val, out_dir, vmin, vmax):
    train_sp, val_sp = .3, .2
    train_idx = int(val['len'] * train_sp)
    val_idx = int(val['len'] * (train_sp + val_sp))
    train_dir = out_dir / 'train'
    Path.mkdir(train_dir, exist_ok=True)
    for window in val['windows'][: train_idx]:
        write_heatmap(window, train_dir, vmin, vmax)
    val_dir = out_dir / 'valid'
    Path.mkdir(val_dir, exist_ok=True)
    for window in val['windows'][train_idx: val_idx]:
        write_heatmap(window, val_dir, vmin, vmax)
    test_dir = out_dir / 'test'
    Path.mkdir(test_dir, exist_ok=True)
    for window in val['windows'][val_idx:]:
        write_heatmap(window, test_dir, vmin, vmax)


def main(fin, write_dir, label, vmin, vmax):
    traffic_windows = []
    try:
        with open(fin) as file:
            for jsonObj in file:
                window = json.loads(jsonObj)
                traffic_windows.append(window)
    except FileNotFoundError:
        print(f'Unable to find file {fin}')

    dist_dict = find_distribution(traffic_windows)
    out_dir = Path(write_dir) / label
    Path.mkdir(out_dir, exist_ok=True, parents=True)
    for val in dist_dict.values():
        if val['len'] == 0:
            continue
        gen_heatmaps(val, out_dir, vmin, vmax)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create a heatmap dataset from a json mongoexport file')
    parser.add_argument('in_file', type=str,
                        help='mongoexport file to read from')
    parser.add_argument('dir', type=str, help='destination folder to write to')
    parser.add_argument(
        'label', type=str,
        help='classification of in_file contents eg. ddos, norm')
    parser.add_argument('--vmin', type=int,
                        help='Minimum traffic seen from devices during normal \
                                activity', default=0)
    parser.add_argument('--vmax', type=int,
                        help='Maximum traffic seen from devices during normal \
                                activity', required=True)
    args = parser.parse_args()
    main(args.in_file, args.dir, args.label, args.vmin, args.vmax)
