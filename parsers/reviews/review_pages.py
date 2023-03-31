from . import *


class ReviewInfo(object):

    debugger = None
     
    def __init__(self):
        self.debugger = logging.getLogger(__name__)
    
    @classmethod
    @catch_exceptions
    def find_urls(self, base_url, url_obj, soup, spec,browser=False):

        if not self.debugger:
            self.debugger = logging.getLogger(__name__)

        self.debugger.crawl_debug("Requesting --> Marketplace %s || Hieararchy %s || Url %s || Page_No %s", spec.get("marketplace"), url_obj.get("hierarchy"), url_obj.get("url"), url_obj.get("page_no"))
        
        selection = soup.select(spec["selector"])
        if not selection:
            return []
        
        next_url= "{}{}".format(url_obj["initial_url"],spec["next_page"].format(url_obj["page_no"]+1))
        review_url_obj = {              
                    "pid": url_obj.get("pid"),
                    "marketplace": spec.get("marketplace"),
                    "type": spec.get("type"),
                    "initial_url":url_obj.get("initial_url"),
                    "url": next_url,
                    "hierarchy": url_obj.get("hierarchy"),
                    "page_no":url_obj["page_no"]+1
        }
        url_obj["soup"]=str(soup)

        file_path=Utils.save_product_info(url_obj, soup, spec)

        review_info_obj = {   
                    "pid": url_obj.get("pid"),           
                    "marketplace": spec.get("marketplace"),
                    "type": spec.get("next_type"),
                    "url": url_obj.get("url"),
                    "hierarchy": url_obj.get("hierarchy"),
                    "file_path": file_path
                }
        
        return [review_url_obj,review_info_obj]

class LazadaReviewInfo(object):

    debugger = None
     
    def __init__(self):
        self.debugger = logging.getLogger(__name__)

    @classmethod
    @catch_exceptions
    def find_urls(self, base_url, url_obj, soup, spec, browser=False):

        if not self.debugger:
            self.debugger = logging.getLogger(__name__)

        self.debugger.crawl_debug("Requesting --> Marketplace %s || Hieararchy %s || Url %s || Page_No %s", spec.get("marketplace"), url_obj.get("hierarchy"), url_obj.get("url"), url_obj.get("page_no"))

        json_content = json.loads(soup.text)
        reviews = []
        
        if json_content["model"]["items"] == None:
            return []
        
        for i in json_content["model"]["items"]:
            json_data = {}
            json_data["rating"] = i["rating"]
            json_data["helpful"] = i["likeCount"]
            json_data["review_title"] = i["reviewTitle"]
            json_data["review_body"] = i["reviewContent"]
            json_data["verified_purchase"] = i["isPurchased"]
            json_data["user_profile"] = i["buyerName"]
            json_data["review_date"] = i["reviewTime"]
            if(i["images"]!=None):
                for j in i["images"]:
                    json_data["review_description_images"]= "https:" + j["url"]
            else:
                json_data["review_description_images"]= "None"
            reviews.append(json_data)


        url_obj["review_details"] = reviews
        url_obj["avg_rating"] = json_content["model"]["ratings"]["average"]
        url_obj["total_rating"] = json_content["model"]["ratings"]["rateCount"]
        url_obj["total_review"] = json_content["model"]["ratings"]["reviewCount"]
        
        review_details={"5" : 0 ,"4" : 0  ,"3" : 0  , "2" : 0  , "1" : 0 }
        index=0

        for key in review_details:
            review_details[key] = json_content["model"]["ratings"]["scores"][index]
            index += 1

        url_obj["page_reviews"] = review_details

        Utils.save_product_info(url_obj,soup,spec)

        next_url= "{}{}".format(url_obj["initial_url"],spec["next_page"].format(url_obj["page_no"]+1))
        review_url_obj = {              
                    "pid": url_obj.get("pid"),
                    "product_link":url_obj.get("product_link"),
                    "marketplace": spec.get("marketplace"),
                    "type": spec.get("type"),
                    "initial_url":url_obj.get("initial_url"),
                    "url": next_url,
                    "hierarchy": url_obj.get("hierarchy"),
                    "page_no": url_obj["page_no"] + 1
        }

        return [review_url_obj]






