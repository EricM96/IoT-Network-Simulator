from requests import get, post
from time import sleep, time
from pymongo import MongoClient
from threading import Thread
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import pprint
import sys


class DataAggregationModule(object):
    router = "http://router:8080/"

    def __init__(self, interval):
        self.interval = interval


class DataCollecter(DataAggregationModule):
    db_username = "root"
    db_password = "password"
    db_url = f"mongodb://{db_username}:{db_password}@db:27017/"

    def __init__(self, label, col_name, interval):
        super.__init__(interval)
        print('establishing mongo connection', flush=True)
        db_client = MongoClient(self.db_url)
        print('Connection established', flush=True)
        db = db_client['traffic_windows']
        self.col = db[col_name]
        self.label = label

    def _write_to_db(self, traffic_window):
        print('starting db insertion', flush=True)
        result = self.col.insert_one(traffic_window)
        print(result, flush=True)

    def main_loop(self):
        while True:
            sleep(self.interval)

            start = time()
            print('Request out', flush=True)
            r = get(self.router)
            end = time()
            delay = end - start

            traffic_window = r.json()
            print('request received:', traffic_window)
            traffic_window['delay'] = delay
            traffic_window['label'] = self.label
            print(traffic_window)
            Thread(target=self._write_to_db, args=(traffic_window, )).run()


class LiveDataTransfer(DataAggregationModule):
    def __init__(self, interval):
        super.__init__(interval)
        self.pp = pprint.PrettyPrinter(sort_dicts=False)

    def main_loop(self):
        while True:
            sleep(self.interval)

            start = time()
            r = get(self.router)
            end = time()
            delay = end - start
            print(r.text, flush=True)

            try:
                traffic_window = r.json()
                self.pp.pprint(traffic_window)
                print(f'Response delay: {delay}', flush=True)
                traffic_window = pd.DataFrame.from_dict(
                    traffic_window, orient='index')
                # _, ax = plt.subplots(1, 1, figsize=(1, 1), dpi=23)
                _ = sns.heatmap(traffic_window, xticklabels=True,
                                yticklabels=True, cbar=False, vmin=0, vmax=100)
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                files = {'img': buffer.getvalue()}
                response = post('http://traffic_analysis:8080/api',
                                files=files)
                prediction = response.text
                print(prediction, flush=True)
            except:
                print(r.status_code)


if __name__ == "__main__":
    assert len(sys.argv) >= 3
    mode, interval = sys.argv[1], int(sys.argv[2])
    if mode == 'live':
        agg_module = LiveDataTransfer(interval)
        agg_module.main_loop()
    elif mode == 'collect':
        label, col_name = sys.argv[3], sys.argv[4]
        agg_module = DataCollecter(label, col_name, interval)
    else:
        print('Select a valid mode and provide necessary arguments',
              flush=True)
