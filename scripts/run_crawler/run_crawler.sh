#!/bin/bash
kill $(ps aux | grep '[Z]+' | awk '{print $2}')
kill $(ps aux | grep '[s]pider.py' | awk '{print $2}')


cd /home/ubuntu/eunimart_data_crawlers
git stash
git fetch origin debug_branch
git checkout debug_branch
git pull origin debug_branch

/usr/bin/python3.6 /home/ubuntu/eunimart_data_crawlers/spider.py -proxy 1 -cmd crawl_site


