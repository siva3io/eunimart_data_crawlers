from . import *

debugger = logging.getLogger(__name__)

class BestSeller(object):

    debugger = None
     
    def __init__(self):
        pass

    @classmethod
    @catch_exceptions
    def find_urls(self, base_url, url_obj, soup, spec,browser=False):
        '''
            this function gets the url as input and gathers all the best seller products for Amazon USA and Amazon India. 
        '''
        debugger.crawl_debug("Requesting --> Marketplace %s || Hieararchy %s || Url %s || Page_No %s", spec.get("marketplace"), url_obj.get("hierarchy"), url_obj.get("url"), url_obj.get("page_no"))
        
        best_seller_products = []
        
        best_sellers_soup = soup.select(spec["discovery_selector"])
        index = 0
        for best_seller in best_sellers_soup :
            selection = best_seller.select(spec["selector"])
            if not selection:
                continue
            url = Utils.make_abs(base_url, selection[0].get("href"))
            pid = str(uuid.uuid4())
            best_seller_parser_obj = {
                        "pid" : pid,        
                        "marketplace": spec.get("marketplace"),
                        "type": spec.get("next_type"),
                        "url": url,
                        "hierarchy": url_obj.get("hierarchy"),
                        "position": index+1,
                }
            index += 1
            best_seller_products.append(best_seller_parser_obj.copy())
        return best_seller_products
    
    @classmethod
    @catch_exceptions
    def find_urls_flipkart(self, base_url, url_obj, soup, spec,browser=False):
        '''
            this function gets the url as input and gathers all the products which has best_selling tag in Flipkart top seller tag in ebay,
            and top rated seller tag in Bonanza. 
        '''

        # debugger.crawl_debug("Request Url %s || Page-----> %s",url_obj["url"])
        print("in fufk")
        product_links = []
        for selector in spec["selector"]:
            product_links_tags = soup.select(selector)
            if product_links_tags:
                break
        print(product_links_tags)
        for index in range(0,len(product_links_tags)):
            url = product_links_tags[index].get("href")

            pid=uuid.uuid4().hex #universal id for eunimart
            meta_data = {
                "pid":pid,
                "marketplace":  spec.get("marketplace"),
                "type": spec.get("next_type"),
                "hierarchy": url_obj["hierarchy"],
                "url":  Utils.make_abs(base_url, url),
                "position": index+1,
            }

            product_links.append(meta_data)
        return product_links
