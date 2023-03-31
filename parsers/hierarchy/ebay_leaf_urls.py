from . import *

class FindLeafUrls:

    debugger = None 

    def __init__(self):
        self.debugger = logging.getLogger(__name__)

    @classmethod
    @catch_exceptions
    def find_urls(self, base_url, url, soup, spec,browser=False):
        """
        Find hierarchy of Ebay based on discovery pattern and download patterns
        """

        if not self.debugger:
            self.debugger = logging.getLogger(__name__)
        
        self.debugger.crawl_debug("Request Hieararchy %s || Url -----> %s",url["hierarchy"],url["url"])

        blinks_class_regexp=re.compile(spec["discovery"]["class"][2])
        blinks_tag_regexp=re.compile(spec["discovery"]["tag"][1])
        b_links = soup.findAll(blinks_tag_regexp, class_=blinks_class_regexp)
        sub_category_tags = []

        if (b_links != []):
            sub_category_tags = [i.find(re.compile(spec["discovery"]["tag"][0]), class_=re.compile(spec["discovery"]["class"][0])) for i in b_links]
            for nosee in soup.find_all(re.compile(spec["discovery"]["tag"][0]), class_=re.compile(spec["discovery"]["class"][1])):
                sub_category_tags.append(nosee)
        else:
            tag_pattern = spec["discovery"]["tag"][0]
            tag_regexp = re.compile(tag_pattern)
            class_regexp1 = re.compile(spec["discovery"]["class"][1])
            sub_category_tags = soup.find_all(tag_regexp, class_=class_regexp1)
            if(len(sub_category_tags) == 2 or len(sub_category_tags) == 1):
                class_regexp = re.compile(spec["discovery"]["class"][0])
            else:
                class_pattern = spec["discovery"]["class"][0]+'|'+spec["discovery"]["class"][1]
                class_regexp = re.compile(class_pattern)
            sub_category_tags = soup.find_all(tag_regexp, class_=class_regexp)
        
        url_objs = []
        
        if sub_category_tags:
            check_url=sub_category_tags[0].attrs['href']
            soup_check = BeautifulSoup(requests.get(check_url).text,"html.parser")
            try:
                current_parent=soup_check.find(re.compile(spec["discovery"]["tag"][0]), class_=re.compile(spec["discovery"]["class"][1])).text
                if current_parent!=url["hierarchy"].split("|")[-1]:
                    next_collection_obj = Utils.save_hierarchy(url, soup, spec)      
                    return [next_collection_obj]
            except:
                 pass
            
            for sub_category_tag in sub_category_tags:
                try:
                
                    if(sub_category_tag):
                        url_obj = Utils.format_hierarchy_link(base_url,url,sub_category_tag,spec)
                        url_objs.append(url_obj)
                    else:
                        self.debugger.crawl_debug("Testing ----> In else Condition")
                     
                except Exception as e:
                    self.debugger.crawl_debug("Exception ----> %s",e)
        self.debugger.crawl_debug("Testing ----> In else Condition")
        return url_objs