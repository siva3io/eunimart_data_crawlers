from . import *

class FindNextPages:
    
    debugger = None 

    def __init__(self):
        self.debugger = logging.getLogger(__name__)
    
    
    @classmethod
    @catch_exceptions
    def find_urls(self, base_url, url_obj, soup, spec,browser=False):
        """ 
        -Vist product pages and discovers all products link and returns products links
        .
        """
        if not self.debugger:
            self.debugger = logging.getLogger(__name__)

        # print("Request Url %s || Page-----> %s",url_obj["url"],url_obj["page_no"])
        self.debugger.crawl_debug("Request Url %s || Page-----> %s",url_obj["url"],url_obj["page_no"])

        class_pattern = '|'.join(spec["discovery"]["class"])
        tag_pattern = '|'.join(spec["discovery"]["tag"])

        class_regexp = re.compile(class_pattern)
        tag_regexp = re.compile(tag_pattern)

        product_links = []
        next_page_no = url_obj["page_no"] + 1
        next_page = "{}{}".format(url_obj["intial_url"],spec["next_page"].format(next_page_no))
        product_links_tags = soup.findAll(tag_regexp, class_=class_regexp)
        self.debugger.crawl_debug("Request Url %s || total number of product_links_tags-----> %s",url_obj["url"],len(product_links_tags))

        for index in range(0,len(product_links_tags)):
            exit_condition =spec.get("exit_condition",[])
            if exit_condition.get("css_selector",[]):  
                # print(exit_condition)    
                selection = soup.select(exit_condition.get("css_selector"))
                if exit_condition.get("find_it",[]): #to check if you want this element or not
                    if selection:
                        break
                
                    
            product_link_obj = Utils.format_tags( base_url, product_links_tags[index], spec )
            if product_link_obj == {}:
                continue
            
            pid=uuid.uuid4().hex #universal id for eunimart
            meta_data = {
                "pid":pid,
                "marketplace":  spec.get("marketplace"),
                "type": spec.get("next_type"),
                "hierarchy": url_obj["hierarchy"],
                "is_best_seller":   product_link_obj.get("is_best_seller",""),
                "url":  product_link_obj.get("product_link",""),
                "position": index+1,
                "page_no":  url_obj["page_no"]
            }

            product_links.append(meta_data)

        self.debugger.crawl_debug("Request Url %s || total number of product_links-----> %s",url_obj["url"],len(product_links))
        if product_links:
            meta_data = {
                "marketplace":spec.get("marketplace"),
                "type":spec.get("type"),
                "hierarchy":url_obj["hierarchy"],
                "page_no":next_page_no,
                "url":next_page,
                "intial_url":url_obj["intial_url"]
            }
            self.debugger.crawl_debug("Requested Url %s || Next Url-----> %s",url_obj["url"], meta_data["url"])
            product_links.append(meta_data)

        return product_links
            

        
        