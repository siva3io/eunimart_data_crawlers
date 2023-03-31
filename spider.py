# spider.py
import re
import os
import sys
import time
import json
import signal
import logging
import argparse
import requests
import test_scripts.file_opener
import queue as BaseQueue

#local imports
import downloader
from config import connect
from datetime import datetime
from url_cache import connect_cache
from parsers import marketplace_parser
from message_queue import connect_message_queue
from parsers.util import Utils,catch_exceptions
from database.models import get_session, create_tables, Products, BestSellerTable, BestSellerTask

COLLECTION_TYPES = [
    "hierarchy", "product_pages", "product_info", "review_info", "product_parser", "review_parser",
    "clean_data", "clean_review_data", 
    "best_seller_info", "best_seller_parser", "clean_best_sellers",
    ]

LISTEN_TYPES = [
    "hierarchy", "product_pages", "product_info", "review_info", "product_parser", "review_parser",
    "best_seller_info", "best_seller_parser"
]

MARKETPLACES = [ 
    "Amazon USA", "Amazon India", "Amazon Canada", "Amazon Australia", "Amazon France", 
    "Amazon Mexico", "Amazon Germany", "Amazon UK", "Amazon Italy", "Amazon Spain", 
    "eBay", "Flipkart", "Etsy", "Bonanza", "Linio Chile", "Linio Columbia", "Linio Mexico", "Linio Peru", 
    "Lazada Thailand", "Lazada Malaysia", "Lazada Singapore", "Lazada Indonesia" 
    ]

TABLE_NAME = {
    "clean_best_sellers":"best_seller",
    "clean_data":"products"

}

COLLECTION_TYPE = "clean_best_sellers"

COLLECTIONS_COUNT = len(COLLECTION_TYPES)
CURRENT_WORKING_DIRECTORY = os.getcwd()

# COLLECTION_TYPE = os.environ.get("COLLECTION_TYPE","hierarchy")

WORKERS = os.cpu_count()

LISTEN_TIMEOUT = 600 # Timeout time to listen other queues instead of give queue

DEBUG_LEVELV_NUM = 35

QUEUE_CHECK_COUNT = 24

intial_count = 0

PROXY = "127.0.0.1:8081"

logging.addLevelName(DEBUG_LEVELV_NUM, "CRAWL_DEBUG")

def custom_debug(self, message, *args, **kws):
    if self.isEnabledFor(DEBUG_LEVELV_NUM):
        # Yes, logger takes its '*args' as 'args'.
        self._log(DEBUG_LEVELV_NUM, message, args, **kws) 

logging.Logger.crawl_debug = custom_debug

Utils.setup_logging()
log = logging.getLogger(name="spider")


with open(os.path.join(CURRENT_WORKING_DIRECTORY, "./specifications/specs.json")) as json_file:
    spec_dic = json.load(json_file)
with open(os.path.join(CURRENT_WORKING_DIRECTORY, "./specifications/seedurls.json")) as json_file:
    seed_url = json.load(json_file)

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    self.kill_now = True

@catch_exceptions
def check_queue(queue, queue_name):
    if queue_name:
        if queue.empty(queue_name):
            sizes = [queue.qsize(qname) for qname in LISTEN_TYPES]
            max_val = max(sizes)
            if max_val == 0:
                return ""
            index_max = sizes.index(max_val)
            queue_name = COLLECTION_TYPES[index_max]    
            ip = requests.get("http://icanhazip.com").text.strip()
            log.info(" IP ADDRESS : %s is Listing to '%s' Queue", ip, queue_name)
    return queue_name
@catch_exceptions
def store_data(session, product_obj):
    new_product_obj = {}
    # print("-->",type(product_obj))
    keys = Products.__table__.columns.keys()
    for key in keys:
        if key != "id":
            if key == "created_date" or key == "updated_date":
                new_product_obj[key] = datetime.utcnow()
                new_product_obj["updated_date"] = datetime.utcnow()
            else:
                new_product_obj[key] = product_obj.get(key, "")
                
    query_obj = session.query(Products.id, Products.created_date).filter(Products.marketplace_id ==  new_product_obj["marketplace_id"]).all()
    if query_obj:
        new_product_obj["id"] = query_obj[0].id
        new_product_obj["created_date"] = query_obj[0].created_date
    product =  Products(**new_product_obj)
    session.merge(product)
    session.commit()
    log.crawl_debug("Stored in db")

@catch_exceptions
def store_best_sellers(session, best_seller_obj):
    new_best_seller_obj = {}
    keys = BestSellerTable.__table__.columns.keys()
    
    for key in keys:
        if key != "id":
            new_best_seller_obj[key] = best_seller_obj.get(key, "")

    best_seller =  BestSellerTable(**new_best_seller_obj)
    session.add(best_seller)
    session.commit()
    log.crawl_debug("Stored in db")


@catch_exceptions
def clean_data(**kwargs):
    queue_name = kwargs.get("queue_name")

    queue = connect_message_queue(names=COLLECTION_TYPES, url=connect["rmq"]["host"])
    
    session = get_session(url=connect["postgress"]["host"])

    create_tables(url=connect["postgress"]["host"], table_name = TABLE_NAME.get(queue_name))

    store ={
        "clean_best_sellers": store_best_sellers,
        "clean_data": store_data
    }

    while True:
        
        url = queue.get(queue_name)
        product_obj = marketplace_parser(url=url, spec=spec_dic[url["marketplace"]][url["type"]])
        store[url["type"]](session, product_obj)


@catch_exceptions
def put_urls(**kwargs):
    collection_type = kwargs.get("queue_name")
    marketplaces = kwargs.get("marketplace",[])
    queue = connect_message_queue(names=[collection_type], url=connect["rmq"]["host"])
    # path_to_json = '/home/ravi/ravi_work/linio_product_info/eunimart_data_crawlers/data'
    # json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.gz')]
    # print(json_files)
    # dic = test_scripts.file_opener.return_json_files(json_files, path_to_json)
    # print(dic)
    # queue.put(collection_type, dic)
    for mk in marketplaces:
        for url in seed_url[mk]:
            queue.put(collection_type, url)


@catch_exceptions
def put_urls_into_queue(**kwargs):

    log.crawl_debug("args %s", kwargs)
    collection_type = kwargs.get("queue_name")

    marketplaces = kwargs.get("marketplace")
    query_filter = {
        "type":collection_type,
        "marketplace":""
    }
    queue = connect_message_queue(names=[collection_type], url=connect["rmq"]["host"])
    session = get_session(url=connect["mysql"]["host"])

    for marketplace in marketplaces:
        log.crawl_debug("Putting Tasks for %s", marketplace)
        query_filter["marketplace"] = marketplace
        tasks = session.query(BestSellerTask).filter_by(**query_filter).all()
        for task in tasks:
            task_obj = task.to_dict()
            task_obj["last_crawled"] = str(task_obj["last_crawled"])
            queue.put(collection_type, task_obj)

    log.crawl_debug("%s Tasks Inserted", len(tasks))

@catch_exceptions
def crawl_site(**kwargs):
    workers = kwargs.get("workers")
    is_proxy = kwargs.get("proxy")
    queue_name = kwargs.get("queue_name")
    listen_queue = kwargs.get("queue_name")

    if is_proxy:
        proxy = PROXY
    else:
        proxy = None

    start_time = time.time()

    killer = GracefulKiller()
    redis_cache = connect_cache(host = connect["redis"]["host"], password=connect["redis"]["password"], port = connect["redis"]["port"], db = connect["redis"]["db"])
    queue = connect_message_queue(names=COLLECTION_TYPES, url=connect["rmq"]["host"])
    dl = downloader.Downloader(workers, 1, cache=redis_cache, proxy=proxy, killer=killer)

    while True:
        if killer.kill_now:
            break
        
        if not queue_name:
            log.crawl_debug("Waiting for Queue")
            time.sleep(300)
        
        listened_time = time.time() - start_time
        
        if listen_queue != queue and listened_time > LISTEN_TIMEOUT:
            queue_name  = listen_queue
            start_time = time.time()

        for _ in range(workers):
            try:
                if "clean" not in queue_name:
                    url = queue.get(queue_name)
                    dl.crawl_page(url, spec_dic[url["marketplace"]][url["type"]], queue)
            except BaseQueue.Empty:
                # The present Queue is empty swithching to next Queue which is has high messages
                queue_name = check_queue(queue, queue_name)
                time.sleep(5)
                break
        time.sleep(2)
    dl.close()

commands = {
    "crawl_site":crawl_site,
    "put_best_sellers":put_urls_into_queue,
    "put_urls":  put_urls,
    "clean_data": clean_data
}


def get_collection_type():
    user_data_path = "/var/lib/cloud/instance/user-data.txt"
    if os.path.exists(user_data_path):
        user_data_obj = open(user_data_path,"r")
        try:
            user_data = json.load(user_data_obj)
        except:
            return COLLECTION_TYPE
        if "type" in user_data:
            return user_data["type"]
        else:
            return COLLECTION_TYPE
    return COLLECTION_TYPE


def parse_args():
    parser = argparse.ArgumentParser(description = "Crawler Runner")
    parser.add_argument("-type", "--collection_type", dest="collection_type", type=str, help="Queue Type to use or listen to", choices=COLLECTION_TYPES, default=get_collection_type())
    parser.add_argument("-env", "--environment", dest="env", help="Environment to run", type=str, default="dev")
    parser.add_argument("-proxy", "--proxy", dest="proxy", help="Whether run with proxy or not choose between 0 or 1", type=int, default=0)
    parser.add_argument("-w", "--workers", dest="workers", help="No_of workers to start", type=int, default=WORKERS)
    parser.add_argument("-m", "--marketplace", dest="marketplace",nargs='*', help="No_of workers to start", type=str, choices=MARKETPLACES , default=MARKETPLACES)
    parser.add_argument("-cmd","--commands", dest="cmds", nargs='*', type=str, help="Command to run", choices=list(commands.keys()))
    args = parser.parse_args()
    return args


def main(arguments):
    params = {
        "queue_name":arguments.collection_type,
        "env":arguments.env,
        "proxy":arguments.proxy,
        "workers":arguments.workers,
        "marketplace":arguments.marketplace
    }
    for i in arguments.cmds:
        command = commands[i]
        print ("Running {}".format(i))
        command(**params)
        

def entry_point():
    args = parse_args()
    main(args)

if __name__ == "__main__":
    entry_point()
      
    
    

     
