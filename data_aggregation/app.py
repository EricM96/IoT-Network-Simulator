from requests import get
from time import sleep, time
from pymongo import MongoClient
from threading import Thread


class DataAggregationModule(object):
    router = "http://router:8080/"
    interval = 15

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


if __name__ == "__main__":
    agg_module = DataAggregationModule('normal')
    agg_module.main_loop()
