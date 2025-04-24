import threading
import random
import time

from multiprocessing.pool import ThreadPool

from utilities import RedisHelper
from services import PetMatchingService
from redis import Redis

from utilities.constants import QUEUE_NAME, ROOT_KEY


def get_input(connection: Redis):
    if QUEUE_NAME == "PET_MATCHER":
        return connection.spop(f"{ROOT_KEY}:lost_pet_reports", 1)
    elif QUEUE_NAME == "NOTIFICATION_REPORT":
        return connection.spop(f"{ROOT_KEY}:notifications", 1)

def extract_remove_data(connection: Redis, key: str):
    target_key = connection.keys(key)

    if len(target_key) > 0:
        target_key_size = connection.scard(target_key[0])

        return connection.sadd(target_key[0], target_key_size)
    
    return []


def main():
    payload = get_input(redis_connection)

    if len(payload) > 0:
        threadlocal = threading.local()
        MAX_WORKERS =  2

        with ThreadPool(MAX_WORKERS) as pool:

            data = pool.map(PetMatchingService, payload)

            del threadlocal
    else:
        print("Got nothing from the queue")



if __name__ == "__main__":
    redis_client = RedisHelper()
    redis_connection = redis_client.redis_connection()
    print(redis_connection, "REDIS CLUSTER CONNECTION")
    while True:
        t1 = time.perf_counter()
        main()
        t2 = time.perf_counter()

        print(f"Finished in {round(t2-t1, 2)}")
        print("Idling...")
        time.sleep(random.randint(2,5))
        