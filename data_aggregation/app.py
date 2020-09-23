from requests import get, post
from time import sleep, time
from pymongo import MongoClient
from threading import Thread
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io


class DataAggregationModule(object):
    router = "http://router:8080/"
    interval = 15


class DataCollecter(DataAggregationModule):
    db_username = "root"
    db_password = "password"
    db_url = f"mongodb://{db_username}:{db_password}@db:27017/"

    def __init__(self, label):
        print('establishing mongo connection', flush=True)
        db_client = MongoClient(self.db_url)
        print('Connection established', flush=True)
        db = db_client['traffic_windows']
        self.col = db['test']
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
    def main_loop(self):
        while True:
            sleep(self.interval)

            r = get(self.router)

            traffic_window = r.json()
            traffic_window = pd.DataFrame.from_dict(
                traffic_window, orient='index')
            # _, ax = plt.subplots(1, 1, figsize=(1, 1), dpi=23)
            _ = sns.heatmap(traffic_window, xticklabels=True,
                            yticklabels=True, cbar=False, vmin=0, vmax=100)
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            with open(buffer.seek(0), 'rb') as data:
                post('http://traffic_analysis/api', data=data)


if __name__ == "__main__":
    agg_module = LiveDataTransfer()
    agg_module.main_loop()
