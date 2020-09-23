from requests import get
from time import sleep, time
from pymongo import MongoClient


ROUTER = "http://router:8080/"
INTERVAL = 15

DB_USERNAME = "root"
DB_PASSWORD = "password"
DB_URL = f"mongodb://{DB_USERNAME}:{DB_PASSWORD}@db:27017/"


def main():
    db_client = MongoClient(DB_URL)
    while True:
        sleep(INTERVAL)

        start = time()
        r = get(ROUTER)
        end = time()
        print(type(r.json()), flush=True)

        print(f"Delay: {end - start:.2f}", flush=True)


if __name__ == "__main__":
    main()
