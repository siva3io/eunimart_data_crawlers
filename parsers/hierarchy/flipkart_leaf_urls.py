from . import *

class FindLeafUrls:
    
    debugger = None 

    def __init__(self):
        self.debugger = logging.getLogger(__name__)
    
    @classmethod
    @catch_exceptions
    def find_urls(self, base_url, url, soup, spec,browser=False):
        """ 
        -Visit category pages till there is no sub-category in it.
        """
        if not self.debugger:
            self.debugger = logging.getLogger(__name__)
        
        self.debugger.crawl_debug("Request Hieararchy %s || Url -----> %s",url["hierarchy"],url["url"])

        class_pattern = '|'.join(spec["discovery"]["class"])
        tag_pattern = '|'.join(spec["discovery"]["tag"])
        download_pattern = '|'.join(spec["download"])

        class_regexp = re.compile(class_pattern)
        tag_regexp = re.compile(tag_pattern)
        download_regexp=re.compile(download_pattern)
        
        category_box = soup.find(tag_regexp,class_=download_regexp)
        if category_box is None:       #check Category box is present
            next_collection_obj = Utils.save_hierarchy(url,soup,spec)      
            return [next_collection_obj]

        sub_category = category_box.find_all(tag_regexp, class_=class_regexp)
        if len(sub_category)==0 :   #reached end
            next_collection_obj = Utils.save_hierarchy(url,soup,spec)      
            return [next_collection_obj]
            
        if url['hierarchy'].split('|')[-1] in  [Utils.format_text(i.text) for i in sub_category]:        #same list as previous page then end
            return []
        
        url_objs = []
        for sub_category_anchor_tag in sub_category:    
                url_obj = Utils.format_hierarchy_link(base_url,url,sub_category_anchor_tag,spec)
                url_objs.append(url_obj)
        
        return url_objs