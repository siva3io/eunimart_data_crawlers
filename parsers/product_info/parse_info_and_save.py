from . import *
class ParseAndSave(object):

    
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
            self.debugger.crawl_debug("Requesting --Marketplace %s || Hieararchy %s || Url -----> %s", spec.get("marketplace"), url_obj.get("hierarchy"), url_obj.get("url"))

            return_list = []
            review_url_obj = {}
            product_parser_obj = {}

            if spec.get("marketplace") and ("Linio" in spec["marketplace"] or "Lazada" in spec["marketplace"]) :
                review_url_final=url_obj["url"]
            else:
                review_url = soup.select(spec["selector"])
                if review_url ==[]:
                    review_url_final=""
                else:
                    review_url_final = Utils.make_abs(base_url,review_url[0].get("href"))
            
            if review_url_final:
                review_url_obj = {   
                    "pid":url_obj.get("pid"),      
                    "page_no":1,
                    "initial_url":review_url_final
                }
                return_list.append(review_url_obj)

            url_obj["soup"]=str(soup)
            file_path = Utils.save_product_info(url_obj, soup, spec)            

            product_parser_obj = { 
                "pid":url_obj.get("pid"),             
                "marketplace": spec.get("marketplace"),
                "type": "product_parser",
                "url": url_obj.get("url"),
                "is_best_seller": url_obj.get("is_best_seller"),
                "position": url_obj.get("position"),
                "page_no":  url_obj.get("page_no"),
                "hierarchy": url_obj.get("hierarchy"),
                "file_path": file_path
            }
            
            if spec.get("marketplace")=="Flipkart":
                listing_id = Utils.get_query_params("lid", url_obj["url"])
                product_id = Utils.get_query_params("pid", url_obj["url"])
                if product_id:
                    review_url_obj["product_id"] = product_id[0]
                    product_parser_obj["product_id"] = product_id[0]
                if listing_id:
                    review_url_obj["listing_id"] = listing_id[0]
                    product_parser_obj["listing_id"] = listing_id[0]

            return_list.append(product_parser_obj)
            # print(review_url_final)
            
            return return_list