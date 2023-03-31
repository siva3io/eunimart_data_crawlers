import os
import json 
import logging
import urllib.parse
import uuid 
from boto.s3.key import Key
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from config import connect
import datetime
import gzip
import boto
import time
from traceback import format_exc
import inspect
import sys
import string

function_return_type = {
    # product parser
    "seller_overall_rating":"",
    "create_json":[],
    "convert_tags_to_dic":[],
    "return_json":{},
    "return_list":[],
    "return_img_links":[],
    "return_img_text":"",
    "return_link":"",
    "marketplace_parser":[],
    "make_abs":"",
    "format_hierarchy_link":"",
    "format_tags":{},
    "format_text":"",
    "save_hierarchy":{},
    "save_product_info":"",
    "get_json":{},


    }


def catch_exceptions(func):
        def wrapped_function(*args, **kargs):
            try:
                
                # if isinstance(args[0], type):
                #     print(args[0])
                   
                
                return func(*args, **kargs)
            except Exception as e:
                l = logging.getLogger(func.__name__)
                
                if(func.__name__=="find_urls"):
                    file_path = args[2].get("file_path","NA")
                    msg = "Marketplace:{} | Url:{} | Type:{} | FilePath:{} | Error:{}".format(args[2]['marketplace'], args[2]['url'], args[2]['type'], file_path, str(e))
                    l.error(msg,exc_info=True)
                if func.__name__ in function_return_type.keys():
                    return function_return_type[func.__name__]
                return e

                
        return wrapped_function



class Utils:
    

    s3_conn = boto.connect_s3(connect['aws']['accessKey'],connect['aws']['accessSecret']) 

    def __init__(self):
        pass

    @classmethod
    @catch_exceptions
    def make_abs(self, base_url, url):
            """
            Make the given URL absolute if it isn't.
            """
            parsed = urllib.parse.urlparse(url)
            if parsed.netloc:
                if "//www.lazada" in url and "https:" not in url:
                    url="https:"+url 
                return url
            else:
                full_url = urllib.parse.urljoin(base_url, url)
                # self.l.crawl_debug("Converted %s into %s", url, full_url)
                return full_url
    
    @classmethod
    @catch_exceptions
    def get_query_params(self,parameter,url):

        parsed = urllib.parse.urlparse(url)
        try:
            return urllib.parse.parse_qs(parsed.query)[parameter]
        except:
            return []
        
    
    @classmethod
    @catch_exceptions
    def format_hierarchy_link(self, base_url, url, sub_category_anchor_tag,spec):
        sub_category_name = self.format_text(sub_category_anchor_tag.text) # Should Reformat the category_name
        sub_category_link = self.make_abs(base_url, sub_category_anchor_tag.attrs['href'])
        new_url = {
            "url":sub_category_link,
            "hierarchy":"{}|{}".format(url["hierarchy"],sub_category_name),
            "marketplace":spec["marketplace"],
            "type":spec["type"],
        }
        return new_url

    @classmethod
    @catch_exceptions
    def format_tags(self, base_url, soup, spec):
        return_data = {}
        
        for css_selector in spec.get("data_selectors",[]):
            for selector in css_selector.get("css_selector",[]):
                selection = soup.select(selector)
                if selection:
                    if  css_selector.get("return_type") == "text":
                        text_data = selection[0].text.strip()
                        return_data[css_selector.get("key")] = text_data
                    elif  css_selector.get("return_type") == "attr_text":
                        alt_data = selection[0][css_selector.get("select_attribute")].strip()
                        return_data[css_selector.get("key")] = alt_data
                    elif css_selector.get("return_type") == "link":
                        url = selection[0]["href"]
                        complete_url = Utils.make_abs(base_url, url)
                        return_data[css_selector.get("key")] = complete_url
        return return_data
    
    @classmethod
    @catch_exceptions
    def format_text(self,inpt_txt):
        return  inpt_txt.replace("\n","").replace("See all in ","") # To add more formart conditions
    
    @classmethod
    @catch_exceptions
    def save_hierarchy(self, url_obj, soup, spec, dl_path='./download/hierarchy'):
            
            meta_data = {
                "marketplace":spec["marketplace"],
                "hierarchy" : url_obj["hierarchy"],
                "url":url_obj["url"],
                "intial_url":url_obj["url"],
                "page_no":1,
                "type":spec["type"],
                "soup":str(soup)
            }
            # self.save_local(url_obj, meta_data, dl_path)
            json_data = json.dumps(meta_data)
            self.upload_to_s3(json_data,spec)
            if meta_data.get("soup"):
                del meta_data["soup"]
            meta_data["type"] = spec.get("next_type")

            return meta_data
    
    @classmethod
    @catch_exceptions
    def save_local(self, url_obj, meta_data, dl_path):
        sub_dir = url_obj["hierarchy"].replace("|","/")
        path = os.path.join(dl_path,sub_dir)
        if not os.path.exists(path):
            os.makedirs(path)
            path = path + "/last_level.json"
            with open(path, 'w+') as outfile:
                json.dump(meta_data, outfile) 
    
    @classmethod
    @catch_exceptions
    def save_product_info(self, url_obj, soup, spec):
        url_obj["next_type"] = spec.get("next_type","")      
        json_data = json.dumps(url_obj)
        file_path=self.upload_to_s3(json_data,spec)
        if url_obj.get("soup"):
            del url_obj["soup"]
        if url_obj.get("next_type"):
            del url_obj["next_type"]
        
        url_obj["type"] = spec.get("next_type")
        return file_path
    
    
    @classmethod
    @catch_exceptions
    def upload_to_s3(self,file_data,spec):
        """
        Uploads files to s3 bucket
        """
        date_object = datetime.date.today()
        file_name = str(date_object)+str(uuid.uuid1())                    #generate random id 
        bucket = self.s3_conn.get_bucket(connect['s3_bucket']['bucket'],validate=False)

        upload_file = boto.s3.key.Key(bucket)
        upload_file.key = spec["marketplace"]+"/"+spec["type"]+"/"+str(file_name)     #path in s3 bucket
        upload_file.content_type = "json"
        compressed_file_data = gzip.compress(bytes(file_data,'utf-8'))
        upload_file.set_contents_from_string(compressed_file_data)
        return spec["marketplace"]+"/"+spec["type"]+"/"+str(file_name)

    @classmethod
    @catch_exceptions
    def download_from_s3(self,path):
        '''
        Download data from s3 bucket
        '''
        data = {}
        bucket = self.s3_conn.get_bucket(connect['s3_bucket']['bucket'])

        key = bucket.get_key(path)
        file_content = key.get_contents_as_string()
        data=json.loads(gzip.decompress(file_content).decode('utf-8'))
      
        return data

    @classmethod
    @catch_exceptions
    def download_folder_s3(self,spec):
        '''
        Download data from s3 bucket
        '''
        

        bucket = self.s3_conn.get_bucket(connect['s3_bucket']['bucket'])
        
        for key in bucket.list(prefix=spec["marketplace"]+"/"+spec["type"]+"/"):
            try:
                print(key)
                file_content = key.get_contents_as_string()
                data = json.loads(gzip.decompress(file_content).decode('utf-8'))

                with open(''+str('op')+".json", 'w+') as f:
                    json.dump(data, f) 
                f.close()
                print("created")
            except Exception as e:
                print(key.name+": Failed",e)

    @classmethod
    @catch_exceptions
    def download_to_local(self,file_path,file_content):
        file_name = str(uuid.uuid1()) + ".json"     
        path = os.path.join(file_path)
        if not os.path.exists(path):
                os.makedirs(path)

        path = path + file_name

        with open(path, 'w+') as outfile:
                json.dump(file_content.decode('utf-8'), outfile)
        return path


    @classmethod
    @catch_exceptions
    def setup_logging(
            default_log_config=None,
            default_level=logging.INFO,
            env_key='LOG_CFG'
        ):
            """Setup logging configuration
            
            Call this only once from the application main() function or __main__ module!
            
            This will configure the python logging module based on a logging configuration
            in the following order of priority:
            
            1. Log configuration file found in the environment variable specified in the `env_key` argument.
            2. Log configuration file found in the `default_log_config` argument.
            3. Default log configuration found in the `logconfig.default_config` dict.
            4. If all of the above fails: basicConfig is called with the `default_level` argument.
            
            Args:
                default_log_config (Optional[str]): Path to log configuration file.
                env_key (Optional[str]): Environment variable that can optionally contain
                    a path to a configuration file.
                default_level (int): logging level to set as default. Ignored if a log
                    configuration is found elsewhere.
        
            Returns: None
            """
            dict_config = None
            logconfig_filename = default_log_config
            env_var_value = os.getenv(env_key, None)

            if env_var_value is not None:
                logconfig_filename = env_var_value

            if connect['logger_config'] is not None:
                dict_config = connect['logger_config']

            # if logconfig_filename is not None and os.path.exists(logconfig_filename):
            #     with open(logconfig_filename, 'rt') as f:
            #         file_config = json.load(f)
            #     if file_config is not None:
            #         dict_config = file_config

            if dict_config is not None:
                logging.config.dictConfig(dict_config)
            else:
                logging.basicConfig(level=default_level)

    
    


class RequestPage(object):
    
    
    def __init__(self):
        """ Init of the client """

        self.session = requests.session()
        self.headers = {
                    'Host': 'www.amazon.in',
                    'User-Agent':"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36",
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    }

    
    @catch_exceptions
    def get(self, url):
        """ GET request with the proper headers """
        ret = self.session.get(url, headers=self.headers)
        if ret.status_code != 200:
            raise ConnectionError(
                'Status code {status} for url {url}\n{content}'.format(
                    status=ret.status_code, url=url, content=ret.text))
        return ret
    
    
    @catch_exceptions
    def check_page(self, html_content):
        """ Check if the page is a valid result page
        (even if there is no result) """
        if "Sign in for the best experience" in html_content:
            valid_page = False
        else:
            valid_page = True
        return valid_page
    
    
    @catch_exceptions
    def get_soup(self, url):
        """
            Will check wether page is valid 
            and then return BeautifulSopu Objet
        """

        response = self.get(url)

        soup = BeautifulSoup(response.content, "html.parser")

        return soup
    
    @catch_exceptions
    def get_json(self,url):
        for _ in range(0,5):
            try:
                return self.get(url).json()
            except ConnectionError as e:
                time.sleep(10)
        return {}

