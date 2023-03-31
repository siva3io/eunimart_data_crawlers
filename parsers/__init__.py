import re
import urllib.parse
import os
import json
import requests
import uuid 
import logging
import string
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from .util import Utils, catch_exceptions
from .hierarchy import find_leaf_urls, ebay_leaf_urls, flipkart_leaf_urls
from .product_pages import find_next_pages
from .product_info import parse_info_and_save
from .product_parsers import product_parsers
from .reviews import review_pages
from .best_selling_info import best_seller
from .clean_data import cleaning_data

all_parser_functions = {

    "Amazon USA":{
        "best_seller_info": best_seller.BestSeller,
        "best_seller_parser": product_parsers.ParseSoup,
        "hierarchy":find_leaf_urls.FindLeafUrls,
        "product_pages":find_next_pages.FindNextPages,
        "product_info": parse_info_and_save.ParseAndSave,
        "product_parser": product_parsers.ParseSoup,
        "review_info": review_pages.ReviewInfo,
        "review_parser":product_parsers.ParseSoup,
        "clean_data": cleaning_data.CleanData,
        "clean_review_data": cleaning_data.CleanData,
        "clean_best_sellers" : cleaning_data.CleanData,
    },
    "Amazon UK":{
        "best_seller_info": best_seller.BestSeller.find_urls,
        "best_seller_parser": product_parsers.ParseSoup.find_urls,
        "hierarchy":find_leaf_urls.FindLeafUrls.find_urls,
        "product_pages":find_next_pages.FindNextPages.find_urls,
        "product_info": parse_info_and_save.ParseAndSave.find_urls,
        "product_parser": product_parsers.ParseSoup.find_urls,
        "review_info": review_pages.ReviewInfo.find_urls,
        "review_parser":product_parsers.ParseSoup.find_urls,
    },
    "Amazon Canada":{
        "hierarchy":find_leaf_urls.FindLeafUrls.find_urls,
        "product_pages":find_next_pages.FindNextPages.find_urls,
        "product_info": parse_info_and_save.ParseAndSave.find_urls,
        "product_parser": product_parsers.ParseSoup.find_urls,
        "review_info": review_pages.ReviewInfo.find_urls,
        "review_parser":product_parsers.ParseSoup.find_urls,
        "clean_data": cleaning_data.CleanData.clean_products


    },
    "Amazon Mexico":{
        "hierarchy":find_leaf_urls.FindLeafUrls.find_urls,
        "product_pages":find_next_pages.FindNextPages.find_urls,
        "product_info": parse_info_and_save.ParseAndSave.find_urls,
        "product_parser": product_parsers.ParseSoup.find_urls,
        "review_info": review_pages.ReviewInfo.find_urls,
        "review_parser":product_parsers.ParseSoup.find_urls,
        "clean_data": cleaning_data.CleanData.clean_products

    },
    "Amazon India":{
        "best_seller_info": best_seller.BestSeller,
        "best_seller_parser": product_parsers.ParseSoup,
        "hierarchy":find_leaf_urls.FindLeafUrls,
        "product_pages":find_next_pages.FindNextPages,
        "product_info": parse_info_and_save.ParseAndSave,
        "product_parser": product_parsers.ParseSoup,
        "review_info": review_pages.ReviewInfo,
        "review_parser":product_parsers.ParseSoup,
        "clean_data": cleaning_data.CleanData,
        "clean_review_data": cleaning_data.CleanData,
        "clean_best_sellers" : cleaning_data.CleanData,
    },
    "Amazon Germany":{
        "hierarchy":find_leaf_urls.FindLeafUrls.find_urls,
        "product_pages":find_next_pages.FindNextPages.find_urls,
        "product_info": parse_info_and_save.ParseAndSave.find_urls,
        "product_parser": product_parsers.ParseSoup.find_urls,
        "review_info": review_pages.ReviewInfo.find_urls,
        "review_parser":product_parsers.ParseSoup.find_urls,
        "clean_data": cleaning_data.CleanData.clean_products

    },
    "Amazon Spain":{
        "hierarchy":find_leaf_urls.FindLeafUrls.find_urls,
        "product_pages":find_next_pages.FindNextPages.find_urls,
        "product_info": parse_info_and_save.ParseAndSave.find_urls,
        "product_parser": product_parsers.ParseSoup.find_urls,
        "review_info": review_pages.ReviewInfo.find_urls,
        "review_parser":product_parsers.ParseSoup.find_urls,
    },
    "Amazon Italy":{
        "hierarchy":find_leaf_urls.FindLeafUrls.find_urls,
        "product_pages":find_next_pages.FindNextPages.find_urls,
        "product_info": parse_info_and_save.ParseAndSave.find_urls,
        "product_parser": product_parsers.ParseSoup.find_urls,
        "review_info": review_pages.ReviewInfo.find_urls,
        "review_parser":product_parsers.ParseSoup.find_urls,
    },
    "Amazon France":{
        "hierarchy":find_leaf_urls.FindLeafUrls.find_urls,
        "product_pages":find_next_pages.FindNextPages.find_urls,
        "product_info": parse_info_and_save.ParseAndSave.find_urls,
        "product_parser": product_parsers.ParseSoup.find_urls,
        "review_info": review_pages.ReviewInfo.find_urls,
        "review_parser":product_parsers.ParseSoup.find_urls,
        "clean_data": cleaning_data.CleanData.clean_products,

    },
    "Amazon Australia":{
        "hierarchy":find_leaf_urls.FindLeafUrls.find_urls,
        "product_pages":find_next_pages.FindNextPages.find_urls,
        "product_info": parse_info_and_save.ParseAndSave.find_urls,
        "product_parser": product_parsers.ParseSoup.find_urls,
        "review_info": review_pages.ReviewInfo.find_urls,
        "review_parser":product_parsers.ParseSoup.find_urls,
        "clean_data": cleaning_data.CleanData.clean_products

    },
    "Etsy":{
        "hierarchy": find_leaf_urls.FindLeafUrls.find_urls,
        "product_pages": find_next_pages.FindNextPages.find_urls,
        "product_info":  parse_info_and_save.ParseAndSave.find_urls,
        "product_parser": product_parsers.ParseSoup.find_urls,
        "review_info": review_pages.ReviewInfo.find_urls,
        "review_parser":product_parsers.ParseSoup.find_urls,
    },
    "Linio Peru":{
        "hierarchy":find_leaf_urls.FindLeafUrls.find_urls,
        "product_pages":find_next_pages.FindNextPages.find_urls,
        "product_info":  parse_info_and_save.ParseAndSave.find_urls,
        "product_parser": product_parsers.ParseSoup.find_urls,
        "review_info": review_pages.ReviewInfo.find_urls,
        "review_parser":product_parsers.ParseSoup.find_urls,
    },
    "Linio Columbia":{
        "hierarchy":find_leaf_urls.FindLeafUrls.find_urls,
        "product_pages":find_next_pages.FindNextPages.find_urls,
        "product_info":  parse_info_and_save.ParseAndSave.find_urls,
        "product_parser": product_parsers.ParseSoup.find_urls,
        "review_info": review_pages.ReviewInfo.find_urls,
        "review_parser":product_parsers.ParseSoup.find_urls,
    },
    "Linio Chile":{
        "hierarchy":find_leaf_urls.FindLeafUrls.find_urls,
        "product_pages":find_next_pages.FindNextPages.find_urls,
        "product_info":  parse_info_and_save.ParseAndSave.find_urls,
        "product_parser": product_parsers.ParseSoup.find_urls,
        "review_info": review_pages.ReviewInfo.find_urls,
        "review_parser":product_parsers.ParseSoup.find_urls,
    },
    "Linio Mexico":{
        "hierarchy":find_leaf_urls.FindLeafUrls.find_urls,
        "product_pages":find_next_pages.FindNextPages.find_urls,
        "product_info":  parse_info_and_save.ParseAndSave.find_urls,
        "product_parser": product_parsers.ParseSoup.find_urls,
        "review_info": review_pages.ReviewInfo.find_urls,
        "review_parser":product_parsers.ParseSoup.find_urls,
    },
    "eBay":{
        "best_seller": product_parsers.ParseSoup.find_urls,
        "hierarchy":ebay_leaf_urls.FindLeafUrls.find_urls,
        "product_pages":find_next_pages.FindNextPages.find_urls,
        "product_info": parse_info_and_save.ParseAndSave.find_urls,
        "product_parser": product_parsers.ParseSoup.find_urls,
        "review_info": review_pages.ReviewInfo.find_urls,
        "review_parser":product_parsers.ParseSoup.find_urls,
    },
    "Flipkart":{
        "best_seller_info": best_seller.BestSeller.find_urls_flipkart,
        "best_seller_parser": product_parsers.ParseSoup.find_urls,
        "hierarchy":flipkart_leaf_urls.FindLeafUrls.find_urls,
        "product_pages":find_next_pages.FindNextPages.find_urls,
        "product_info": parse_info_and_save.ParseAndSave.find_urls,
        "product_parser": product_parsers.ParseSoup.find_urls,
        "review_info": review_pages.ReviewInfo.find_urls,
        "review_parser":product_parsers.ParseSoup.find_urls,
        "clean_data": cleaning_data.CleanData.clean_products,
        "clean_review_data": cleaning_data.CleanData.clean_reviews,
    },
    "Bonanza":{
        "best_seller_info": best_seller.BestSeller.find_urls_flipkart,
        "best_seller_parser": product_parsers.ParseSoup.find_urls,
        "clean_best_sellers" : cleaning_data.CleanData.clean_products,
        "hierarchy":flipkart_leaf_urls.FindLeafUrls.find_urls,
        "product_pages":find_next_pages.FindNextPages.find_urls,
        "product_info": parse_info_and_save.ParseAndSave.find_urls,
        "product_parser": product_parsers.ParseSoup.find_urls,
        "review_info": review_pages.ReviewInfo.find_urls,
        "review_parser":product_parsers.ParseSoup.find_urls,
        "clean_data": cleaning_data.CleanData.clean_products,
        "clean_review_data": cleaning_data.CleanData.clean_reviews,
    },
    "Lazada Thailand":{
        "hierarchy":find_leaf_urls.FindLeafUrls.find_urls,
        "product_pages":find_next_pages.FindNextPages.find_urls,
        "product_info": parse_info_and_save.ParseAndSave.find_urls,
        "product_parser": product_parsers.ParseSoup.find_urls,
        "review_info": review_pages.LazadaReviewInfo.find_urls
    },
    "Lazada Malaysia":{
        "hierarchy":find_leaf_urls.FindLeafUrls.find_urls,
        "product_pages":find_next_pages.FindNextPages.find_urls,
        "product_info": parse_info_and_save.ParseAndSave.find_urls,
        "product_parser": product_parsers.ParseSoup.find_urls,
        "review_info": review_pages.LazadaReviewInfo.find_urls
    },
    "Lazada Singapore":{
        "hierarchy":find_leaf_urls.FindLeafUrls.find_urls,
        "product_pages":find_next_pages.FindNextPages.find_urls,
        "product_info": parse_info_and_save.ParseAndSave.find_urls,
        "product_parser": product_parsers.ParseSoup.find_urls,
        "review_info": review_pages.LazadaReviewInfo.find_urls
    },
    "Lazada Indonesia":{
        "hierarchy":find_leaf_urls.FindLeafUrls.find_urls,
        "product_pages":find_next_pages.FindNextPages.find_urls,
        "product_info": parse_info_and_save.ParseAndSave.find_urls,
        "product_parser": product_parsers.ParseSoup.find_urls,
        "review_info": review_pages.LazadaReviewInfo.find_urls
    }
    
}

@catch_exceptions
def marketplace_parser(base_url="",url={},soup=None,spec={},browser=False):
    obj = all_parser_functions[spec['marketplace']][spec['type']]()
    if spec['type'] == "clean_data" or spec['type'] == "clean_best_sellers" :
        return obj.clean_products(base_url,url,soup,spec,browser) 
    elif spec['type'] == "clean_review_data":
        return obj.clean_reviews(base_url,url,soup,spec,browser) 
    return obj.find_urls(base_url,url,soup,spec,browser) 