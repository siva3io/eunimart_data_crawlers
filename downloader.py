import os
import re
import json
import time
import logging
import requests
import itertools
import w3lib.url
import urllib.parse
import selenium.webdriver


from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool, threading

# Local import
from parsers import marketplace_parser # This Pacakge Contains All types of Parsers per marketplace
from parsers.util import catch_exceptions


class Downloader:

    def __init__(self, disc_workers, dl_workers=None, cache=None, proxy=None, killer=""):
        self.l = logging.getLogger(name="Downloader")
        self.PROXY = proxy
        dl_workers = disc_workers if not dl_workers else dl_workers
        # TODO: Separate browsers might mess up auth data. We might
        # need to login on all the browsers before doing this.
        self.l.info("Starting %d browsers for discovery", disc_workers)
        self.d_browsers = []
        for _ in range(disc_workers):
            browser = self.create_browser()
            self.d_browsers.append(browser)
        self.d_browser_pool = itertools.cycle(self.d_browsers)
        # self.l.crawl_debug("Starting %d workers for discovery", disc_workers)
        self.discovery_pool = ThreadPool(disc_workers)
        
        self.cache = cache

        self.killer = killer

        self.start_time = time.time()
        self.refresh_time_out = 180

        # self.refresh_thread = threading.Thread(target=self.refresh_function)
        # self.refresh_thread.start()

    def create_browser(self):
        chrome_options = selenium.webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('disable-infobars')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--incognito')
        chrome_options.add_argument('--start-maximized')
        if self.PROXY:
            chrome_options.add_argument('--proxy-server=http://%s' % self.PROXY)
        proxy_browser = selenium.webdriver.Chrome(chrome_options=chrome_options)
        proxy_browser.set_page_load_timeout(40)
        return proxy_browser

    @catch_exceptions
    def restart_browser(self, previous_browser):
        
        browser = self.create_browser()
        self.d_browsers.remove(previous_browser)
        self.d_browsers.append(browser)
        previous_browser.quit()
        self.d_browser_pool = itertools.cycle(self.d_browsers)
        return browser

    @catch_exceptions
    def fetched(self, url):
        url = w3lib.url.canonicalize_url(url)
        if not self.cache.get(url):
            self.cache.set(url, 'true')
            return False
        else:
            return True
    
    @catch_exceptions
    def refresh_function(self):
        while True:
            time.sleep(60)
            if self.killer.kill_now:
                break
            time_lasted = time.time() - self.start_time

            if time_lasted > self.refresh_time_out:
                self.refresh_browsers()
                self.start_time = time.time()


    @catch_exceptions
    def refresh_browsers(self):
        for _ in range(len(self.d_browsers)):
            try:
                browser = next(self.d_browser_pool)
                try:
                    browser.refresh()
                    break
                except:
                    browser = self.restart_browser(browser)
                    self.l.error("Got timeout error Restarting browser")
                self.l.crawl_debug("Refreshing the browsers")
            except Exception as e:
                self.l.error("This is the error %s", e, exc_info=True)


    @catch_exceptions
    def crawl_page(self, url, spec, queue, dl_path=""):
        """
        Download the given URL and parse it as per spec.

        - All URLs that match spec['discovery'] regexp will be put into
          the queue for further discovery

        - All URLs that match spec['download'] regexp will be
          downloaded into the directory specified by dl_path
        """
        
        def perform_actions(browser, spec):
            try:
                data = browser.page_source
                soup = BeautifulSoup(data, 'html.parser')
                
                str_soup = str(soup)
                
                if "ERR_PROXY_CONNECTION_FAILED" in str_soup:
                    browser.delete_all_cookies()
                    self.l.error("Got %s error and message","ERR_PROXY_CONNECTION_FAILED")
                    return None
                elif "ERR_INCOMPLETE_CHUNKED_ENCODING" in str_soup:
                    browser.delete_all_cookies()
                    self.l.error("Got %s error and message","ERR_INCOMPLETE_CHUNKED_ENCODING")
                    return None
                elif "ERR_CONNECTION_TIMED_OUT" in str_soup:
                    browser.delete_all_cookies()
                    self.l.error("Got %s error and message","ERR_CONNECTION_TIMED_OUT")
                    return None
                elif "ERR_EMPTY_RESPONSE" in str_soup:
                    browser.delete_all_cookies()
                    self.l.error("Got %s error and message","ERR_EMPTY_RESPONSE")
                    return None
                elif "ERR_CONNECTION_CLOSED" in str_soup:
                    browser.delete_all_cookies()
                    self.l.error("Got %s error and message","ERR_CONNECTION_CLOSED")
                    return None
                elif "Sorry! Something went wrong!" in str_soup:
                    browser.delete_all_cookies()
                    self.l.error("Got %s error and message","Sorry! Something went wrong!")
                    return None

                elif "Enter the characters you see below"   in str_soup:
                    browser.delete_all_cookies()
                    self.l.error("Got %s error and message","Enter the characters you see below")
                    return None
            except Exception as e:
                self.l.error("Error in getting page source %s", e)
                return None

            
            if("click" in spec["actions"]):
                try:
                    element = browser.find_element_by_class_name(spec["actions"]["click"]["class"])  #click see all button
                    element.click()
                except Exception as e:
                    #It Will thorgh error if that button is not present,So, just ignore
                    self.l.warning("In Exception %s",e)
                    pass
            
            if("wait" in spec["actions"]):
                content = None
                while not content:  #check until the  content loads
                    try:    
                        content=browser.find_element_by_class_name(spec["actions"]["wait"]["class"])
                    except:
                        #It Will error if the class is not yet loaded
                        pass
            
            if "scroll" in spec["actions"]:
                last_height = browser.execute_script("return document.body.scrollHeight")
                while True:
                    # Scroll down to bottom
                    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                    # Wait to load page
                    time.sleep(spec["actions"]["scroll"]["time"])

                    # Calculate new scroll height and compare with last scroll height
                    new_height = browser.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
            if "click_by_css" in spec["actions"]:
                for _ in range(spec["actions"]["click_by_css"]["no_of_clicks"]):
                    try:                  
                        time.sleep(3)
                        element = browser.find_element_by_css_selector(spec["actions"]["click_by_css"]["selector"])
                        browser.execute_script("arguments[0].click();", element)
                    except Exception as e:
                        self.l.warning("In Exception %s",e) 
                        pass
            try:
                data = browser.execute_script("return document.body.innerHTML")
                soup = BeautifulSoup(data, 'html.parser')
                return soup
            except Exception as e:
                self.l.error("Error in getting html page %s", e)
                return None

            

        @catch_exceptions
        def get_response(url, spec, browser):
            soup = None
            success = False
            for i in range(10):
                try:
                    browser.get(url["url"])
                except:
                    self.l.error("Got timeout error retrying this url %s", url["url"])
                    # browser = next(self.d_browser_pool)
                    break
                    # browser = self.restart_browser(browser)
                    # browser.get(url["url"])
                    
                soup = perform_actions(browser, spec)
                if soup:
                    success = True
                    break
                else:
                    time.sleep(3)
                    self.l.crawl_debug("***************** Retrying again %s ********************", i)
            return soup, success
        
        @catch_exceptions
        def process_thread(browser, url):
            try:
                crnt_url = browser.current_url
                
                if not self.killer.kill_now:
                    self.l.crawl_debug("Request queue obj ---> %s", url)
                    split_url = urllib.parse.urlsplit(url["url"])
                    base_url = "{}://{}".format(split_url.scheme, split_url.hostname)
                    if spec["type"] in ["clean_best_sellers", "product_parser", "review_parser", "clean_data", "clean_review_data"]:
                        soup = "For these no Soup is required"
                        success = True
                    else:
                        soup, success = get_response(url, spec, browser)
                        time.sleep(3)
                    if soup and success:
                        return_list = marketplace_parser(base_url, url, soup, spec, browser)
                        # self.l.crawl_debug("----> %s Is Size <------", base_url))
                        for i in return_list:
                            
                            if i["marketplace"] in ["eBay"]:   
                                url_string = "{}|{}".format(i["type"],i["url"])
                            else:
                                url_string = "{}|{}|{}".format(i["hierarchy"],i["type"],i["url"])
                             
                            if i.get("success",True) and not self.fetched(url_string):
                                self.l.crawl_debug(" Requeueing %s for rediscovery", i)
                                self.l.crawl_debug(" Requeueing %s for rediscovery", i['type'])
                                
                                queue.put(i["type"],i)
                            elif not i.get("success",True):
                                self.l.crawl_debug("Url Failed so requeing obj ---> %s", url)
                                queue.put(url["type"],i)
                            else:
                                self.l.crawl_debug(" %s already processed", i)
                    else:
                        self.l.crawl_debug("Url Failed so requeing obj ---> %s", url)
                        queue.put(url["type"],url)
                else:
                    self.l.crawl_debug("Got Kill Signal Requeueing %s into Queue", url)
                    queue.put(url["type"],url)
            except Exception:
                self.l.crawl_debug("Browser is not working so requeing obj ---> %s", url)
                queue.put(url["type"],url)

        browser = next(self.d_browser_pool)
        try:
            current_url = browser.current_url
        except:
            browser = self.restart_browser(browser)
            self.l.crawl_debug("restared the browser")
        # process_thread(browser, url)
        self.discovery_pool.apply_async(process_thread, args=(browser, url))


    @catch_exceptions
    def close(self):
        self.discovery_pool.close()
        self.discovery_pool.join()
        # self.refresh_thread.join()
        # self.download_pool.close()
        # self.download_pool.join()
        for a in self.d_browsers:
            a.quit()
        # for a in self.g_browsers:
        #     a.quit()
