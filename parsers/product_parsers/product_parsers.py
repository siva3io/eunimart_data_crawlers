from . import *
from selenium.common.exceptions import WebDriverException

class ParseSoup(object):
    return_functions = {}
    create_json_functions = {}

    debugger = None 

    def __init__(self):
        self.debugger = logging.getLogger(__name__)
    
    @classmethod
    @catch_exceptions
    def perform_actions(self, browser, page_source=False):
        try:
            data = browser.page_source
            soup = BeautifulSoup(data, "html.parser")
            str_soup = str(soup)
            
            if "ERR_PROXY_CONNECTION_FAILED" in str_soup:
                browser.delete_all_cookies()
                self.debugger.error("Got %s error and message","ERR_PROXY_CONNECTION_FAILED")
                return None
            elif "ERR_INCOMPLETE_CHUNKED_ENCODING" in str_soup:
                browser.delete_all_cookies()
                self.debugger.error("Got %s error and message","ERR_INCOMPLETE_CHUNKED_ENCODING")
                return None
            elif "ERR_SOCKET_NOT_CONNECTED" in str_soup:
                browser.delete_all_cookies()
                self.debugger.error("Got %s error and message","ERR_SOCKET_NOT_CONNECTED")
                return None
            elif "ERR_CONNECTION_TIMED_OUT" in str_soup:
                    browser.delete_all_cookies()
                    self.debugger.error("Got %s error and message","ERR_CONNECTION_TIMED_OUT")
                    return None
            elif "ERR_EMPTY_RESPONSE" in str_soup:
                self.debugger.error("Got %s error and message","ERR_EMPTY_RESPONSE")
                return None
            elif "ERR_CONNECTION_CLOSED" in str_soup:
                browser.delete_all_cookies()
                self.debugger.error("Got %s error and message","ERR_CONNECTION_CLOSED")
                return None
            elif "Sorry! Something went wrong!" in str_soup:
                browser.delete_all_cookies()
                self.debugger.error("Got %s error and message","Sorry! Something went wrong!")
                return None
            elif "Enter the characters you see below"   in str_soup:
                browser.delete_all_cookies()
                self.debugger.error("Got %s error and message","Enter the characters you see below")
                return None
            elif page_source:
                return soup
            else:
                data = browser.execute_script("return document.body.innerHTML")
                soup = BeautifulSoup(data, "html.parser")
                return soup
        except Exception as e:
            self.debugger.error("Error in getting page source %s", e)
            return None

    @classmethod
    @catch_exceptions
    def get_soup(self, url, browser, page_source=False):
        soup = None
        success = False
        for i in range(10):
            try:
                browser.get(url)
            except Exception as e:
                self.debugger.error("Got timeout error %s and message is %s", url, e)
                break
            soup = self.perform_actions(browser, page_source)
            if soup:
                success = True
                break
            else:
                self.debugger.crawl_debug("***************** Retrying again %s ********************", i)
            time.sleep(1.5)
        return soup, success

    @classmethod
    @catch_exceptions
    def seller_overall_rating(self, tr_tags, css_selector, base_url, browser):
        seller_rating = {"30_days": {}, "90_days": {}, "120_days": {}, "life_time": {}}

        intravels = ["", "30_days", "90_days", "120_days", "life_time"]

        for row in tr_tags[1:]:
            td_tags = row.findAll(css_selector["value"])
            if td_tags:
                key_name = td_tags[0].text.strip().lower()
                for index in range(1, len(td_tags)):
                    if seller_rating[intravels[index]].get(key_name):
                        seller_rating[intravels[index]][key_name] = td_tags[index].text.strip().lower()
                    else:
                        seller_rating[intravels[index]][key_name] = {}
                        seller_rating[intravels[index]][key_name] = td_tags[index].text.strip().lower()
        return seller_rating

    @classmethod
    @catch_exceptions
    def convert_tags_to_dic(self, tags, json_specs, base_url, browser):
        list_of_dic = []

        for tag in tags:
            dic_obj = {}
            for json_spec in json_specs:
                json_spec_params = self.form_params(json_spec, base_url)
                css_data = self.css_select(browser, tag, json_spec_params)
                if not css_data:
                    dic_obj[json_spec["key"]] = "This {} css_selector not found".format(json_spec["css_selector"])
                elif json_spec["save"]:
                    dic_obj[json_spec["key"]] = css_data
            list_of_dic.append(dic_obj)
        return list_of_dic

    @classmethod
    @catch_exceptions
    def create_json(self, tags, json_specs, base_url, browser):
        return self.convert_tags_to_dic(tags, json_specs, base_url, browser)

    
    @classmethod
    @catch_exceptions
    def return_json(self, browser, selection=None, **kwargs):
        """

        :param selection: list of soup objects
        :param json_selector: list of specs and each spec contain what css_selector to select.
        :param use_function: It specifies which function to use for create json
        :return: dictionary of data which is converted from html to dictionary
        """
        json_selector = kwargs.get("json_selector")
        use_function = kwargs.get("use_function")
        base_url = kwargs.get("base_url")
        return self.create_json_functions[use_function](selection, json_selector, base_url, browser)

    @classmethod
    @catch_exceptions
    def create_request(self, base_url, params, browser):
        """
            This function is used for to create request url with all parameter
            use this function only for Amazon
        """
        return_data = []

        if params==[]:
            return ""
        request_params = params["ajax"]["params"]
        request_params[params["ajax"]["id_param_name"]] = ",".join(params["ajax"]["id_list"])
        request_params["count"] = 1
        request_params["offset"] = 0
        request_parms = urlencode(request_params)
        url = "{}{}?{}".format(base_url, params["ajax"]["url"], request_parms)

        # req_obj = RequestPage()

        soup, success = self.get_soup(url, browser, page_source=True)
        
        if not success:
            return []
        args = {
            "css_selector": ["pre"],
            "return_type": "text"
        }
        css_data = self.css_select(browser, soup, args)
        
        try:
            json_data = json.loads(css_data)["data"]
        except:
            self.debugger.error("url ---> %s",url)
            return []

        for data in json_data:
            try:
                soup_obj = BeautifulSoup(data, "html.parser") 
                return_data.append(soup_obj)
            except:
                # Nothing to worry some time data contains invalid or extra
                # html tags for scripts which can't be parsed to handle that case.
                pass
        return return_data

    @classmethod
    @catch_exceptions
    def return_text(self, browser, selection=None, **kwargs):
        """

        :param selection: list of soup objects.
        :param index: index to selected from the list.
        :param delete_tag: The tag to found and deleted from soup.
        :return: It returns text from  soup Object
        """
        index = kwargs.get("index", 0)
        delete_tag = kwargs.get("delete_tag")
        if isinstance(selection, list):
                selection = selection[index]

        if hasattr(selection, 'text'):
            if delete_tag:
                if selection.find(delete_tag):
                    selection.find(delete_tag).decompose()
            return selection.text.strip()
        return ""

    @classmethod
    @catch_exceptions
    def return_link(self, browser, selection=None, **kwargs):
        """

        :param selection: list of soup objects.
        :param base_url: base url is ex: https://amazon.in or https://www.ebay.com
        :param index: index to selected from the list.
        :param select_attribute: the attribute which is to be selected from tag ex: "href","src"
        :return: absolute url
        """
        base_url = kwargs.get("base_url")
        index = kwargs.get("index", 0)
        select_attribute = kwargs.get("select_attribute", "href")

        url = selection[index][select_attribute]
        url = Utils.make_abs(base_url, url)
        return url

    @classmethod
    @catch_exceptions
    def return_content(self, browser, selection, **kwargs):
        """

        :param selection: list of soup objects.
        :param index: index to selected from the list.
        :return: soup content present in that index
        """
        index = kwargs.get("index", 0)

        return selection[index]


    @classmethod
    @catch_exceptions
    def return_list(self, browser, selection=None, **kwargs):
        """

        :param selection: list of soup object
        :return: "|" joined string, extracted text from each soup object
        """

        return "|".join([data.text.strip() for data in selection])

    @classmethod
    @catch_exceptions
    def return_img_links(self, browser, selection=None, **kwargs):
        """

        :param selection: list of soup objects.
        :param select_attribute: the attribute which is to be selected from tag ex: "href","src"
        :return: "|" joined string, extracted select_attribute from each soup object
        """

        select_attribute = kwargs.get("select_attribute", "src")

        return "|".join([data[select_attribute] for data in selection])

    @classmethod
    @catch_exceptions
    def return_img_text(self, browser, selection=None, **kwargs):
        """

        :param selection: list of soup objects.
        :param index: list of soup objects.
        :param select_attribute: the attribute which is to be selected from tag ex: "alt","itemprop"
        :return: text present inside of soup attribute
        """

        select_attribute = kwargs.get("select_attribute", "alt")
        index = kwargs.get("index", 0)

        return selection[index][select_attribute].strip()

    @classmethod
    @catch_exceptions
    def return_special_content(self, browser, selection=None, **kwargs):
        """

        :param selection: list of soup objects.
        :param base_url: ex: https://amazon.in or https://www.ebay.com
        :param index: list of soup objects.
        :param select_attribute: the attribute which is to be selected from tag
        :return: list of soup objects
        """
        base_url = kwargs.get("base_url")
        index = kwargs.get("index", 0)
        select_attribute = kwargs.get("select_attribute", "data-a-carousel-options")

        return self.create_request(base_url, json.loads(selection[index].get(select_attribute,"")),browser)

    @classmethod
    @catch_exceptions
    def css_select(self, browser, soup=None, params={}):
        """ Returns the content of the element pointed by the CSS selector,
        or an empty string if not found """
        selection = []
        return_data = ""

        for css_selector in params.get("css_selector"):
            if params.get("return_same"):
                selection = soup
            else:
                selection = soup.select(css_selector)
                # print(selection)
            if selection:
                return_data = self.return_functions[params.get("return_type")](browser , selection, **params)
                break
        return return_data

    @classmethod
    @catch_exceptions
    def form_params(self, spec, base_url=None):
        params = {}
        required_params = ["css_selector", "return_type", "json_selector", "use_function", "return_same", "delete_tag","select_attribute", "index"]
        for required_param in required_params:
            if spec.get(required_param):
                params[required_param] = spec.get(required_param)
        if base_url:
            params["base_url"] = base_url
        return params

    @classmethod
    @catch_exceptions
    def collect_info(self, soup, base_url, spec, browser, product_details):
        css_content = None
        
        if soup:
            css_content = self.css_select(browser,soup, self.form_params(spec, base_url))

        if not css_content:
            product_details[spec["key"]] = "This {} css_selector not found".format(spec["css_selector"])

        elif spec["next_selectors"]:
            if spec["return_type"] == "link":
                css_content, success = self.get_soup(css_content,browser)
                if not success:
                    product_details["success"] = False
            if css_content:
                for specification in spec["next_selectors"]:
                    self.collect_info(css_content,base_url, specification,browser,product_details)
        elif spec["save"]:
            product_details[spec["key"]] = css_content

    @classmethod
    @catch_exceptions
    def find_urls(self, base_url, url_obj, soup, spec, browser=None):
        
        product_details = {}

        self.return_functions = {
            "text": self.return_text,
            "link": self.return_link,
            "content": self.return_content,
            "json": self.return_json,
            "list": self.return_list,
            "img_links": self.return_img_links,
            "img_text": self.return_img_text,
            "special_content": self.return_special_content,
        }
        self.create_json_functions = {
            "seller_overall_rating": self.seller_overall_rating,
            "create_json": self.create_json  
        }

        if not self.debugger:
            self.debugger = logging.getLogger(__name__)
        
        self.debugger.crawl_debug("Requesting --Marketplace %s || Hieararchy %s || Url -----> %s", spec.get("marketplace"), url_obj.get("hierarchy"), url_obj.get("file_path"))

        try:
            crnt_url = browser.current_url
        except Exception:
            url_obj["success"] = False
            return [url_obj]
            
        s3_file_path = url_obj.get("file_path","")
        if s3_file_path != "" :
            data = Utils.download_from_s3(s3_file_path)    
            soup = BeautifulSoup(data["soup"], "html.parser")
        
        for selection in spec["selections"]:
            self.collect_info(soup, base_url, selection, browser=browser, product_details=product_details)

        if not product_details.get("success",True):
            url_obj["success"] = False
            return [url_obj]

        url_obj["product_details"] = product_details
        
        
        file_path = Utils.save_product_info(url_obj,soup,spec)
        
        url_obj["type"] = spec["next_type"] 
        url_obj["file_path"] = file_path
        self.debugger.crawl_debug("Saved File --Marketplace %s || Hieararchy %s || Url -----> %s", spec.get("marketplace"), url_obj.get("hierarchy"), file_path)
        del url_obj["product_details"]
        url_obj["success"] = True
        return [url_obj]



# open("centerCol.html","w+").write(center_col)
