from . import *
class FindLeafUrls:
    
    debugger = None 

    def __init__(self):
        self.debugger = logging.getLogger(__name__)
    
    @classmethod
    @catch_exceptions
    def check_for_download(self, sub_cat_anchor_tags, download_page,spec ):
        if (
                (
                    not sub_cat_anchor_tags 
                        and 
                    download_page 
                        and  
                    spec["marketplace"] != "Amazon USA" 
                        and  
                    "Amazon" in spec["marketplace"]
                ) 
                    or
                (    
                    download_page
                        and
                    "Linio" in spec["marketplace"] 
                )

            ):
            return True
        return False

    @classmethod
    @catch_exceptions
    def find_urls(self, base_url, url, soup, spec,browser=False):
        """
        Find hierarchy of Amazaon based on discovery pattern
        """
        if not self.debugger:
            self.debugger = logging.getLogger(__name__)
        self.debugger.crawl_debug("Requesting --> Marketplace %s || Hieararchy %s || Url -----> %s", spec["marketplace"], url["hierarchy"], url["url"])

        if "Lazada" in spec["marketplace"]:
            next_collection_obj = Utils.save_hierarchy(url,soup,spec)
            return [next_collection_obj]
        if "class" in spec["exit_condition"] and "tag" in spec["exit_condition"]:
            
            exit_class_regexp = re.compile('|'.join(spec["exit_condition"]["class"]))
            exit_tag_regexp = re.compile('|'.join(spec["exit_condition"]["tag"]))
            if soup.find(exit_tag_regexp, class_=exit_class_regexp):
                return []
        
        class_pattern = '|'.join(spec["discovery"]["class"])
        tag_pattern = '|'.join(spec["discovery"]["tag"])
        download_pattern = '|'.join(spec["download"])
        
        class_regexp = re.compile(class_pattern)
        tag_regexp = re.compile(tag_pattern)
        download_regexp = re.compile(download_pattern)
        
        sub_category_tags = soup.find_all(tag_regexp, class_=class_regexp)
        download_page = soup.find(tag_regexp,class_=download_regexp)
        
        sub_cat_anchor_tags =[]

        if "Linio" in spec["marketplace"] and sub_category_tags :
            sub_category_tags = [ sub_category_tags[-1] ]
            download_page = sub_category_tags[0].find(tag_regexp,class_=download_regexp)
            
        if sub_category_tags : 
            for sub_category_tag in sub_category_tags:
                a_tags = sub_category_tag.find_all('a')
                
                if "Linio" in spec["marketplace"] :
                    a_tags = a_tags[1:]
                
                for a_tag in a_tags:
                    sub_cat_anchor_tags.append(a_tag)

            if self.check_for_download(sub_cat_anchor_tags, download_page,spec):    
                next_collection_obj = Utils.save_hierarchy(url,soup,spec)      
                return [next_collection_obj]

        elif download_page :
            next_collection_obj = Utils.save_hierarchy(url,soup,spec)      
            self.debugger.crawl_debug("in download page %s || Hieararchy %s || Url -----> %s", spec["marketplace"], url["hierarchy"], str(next_collection_obj))
            return [next_collection_obj]
        else:
            self.debugger.crawl_debug("no download page and no sub_category_tags %s || Hieararchy %s ", spec["marketplace"], url["hierarchy"])

            return []

        url_objs = []
 
        for sub_category_anchor_tag in sub_cat_anchor_tags:
            try:
                
                if(sub_category_anchor_tag):
                    url_obj = Utils.format_hierarchy_link(base_url,url,sub_category_anchor_tag,spec)
                    url_objs.append(url_obj)
                else:
                    self.debugger.crawl_debug("Testing ----> In else Condition") # N: Use the logger here. 
                     
            except Exception as e:
                self.debugger.crawl_debug("Exception ----> %s",e)
        # self.l.crawl_debug("Testing ----> %s",url_objs)
        return url_objs