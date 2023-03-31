from . import *
import urllib.parse

class CleanData(object):

        debugger = None 

        clean_return_functions = {}


        def __init__(self):
            self.debugger = logging.getLogger(__name__)
        
            
        @classmethod
        @catch_exceptions
        def split_hierarchy(self, url_obj):

            '''calling split hierarchy for splitting hierarchy and deleting the hierarchy key'''

            sub_categories = url_obj.get("hierarchy", "").split("|")
            for i in range(len(sub_categories), 9):
                sub_categories.append("")
            url_obj["category"] = sub_categories[0]
            for i in range(1, len(sub_categories)):
                url_obj["sub_category_{}".format(i)] = sub_categories[i]
            del url_obj["hierarchy"]


        @classmethod
        @catch_exceptions
        def split_images(self, spec, url_obj, parent_key, child_key):

            '''calling split images for splitting images and deleting the images key'''

            sub_categories = url_obj.get(parent_key, "").split("|")

            for i in range(len(sub_categories), 9):
                sub_categories.append("")
            for i in range(0, len(sub_categories)):
                if "HomeCustomProduct" in sub_categories[i] or ".svg" in sub_categories[i] or ".gif" in sub_categories[i] or "play-icon" in sub_categories[i]:
                    continue
                if re.findall(spec["keys"][parent_key]["clean_regex"]["regex"], sub_categories[i]) == []:
                    url_obj[child_key.format(i+1)] = sub_categories[i]  
                else:
                    url_obj[child_key.format(i+1)] = sub_categories[i].replace(re.findall(spec["keys"][parent_key]["clean_regex"]["regex"], sub_categories[i])[0], ".")                        
            del url_obj[parent_key]


        @catch_exceptions
        def unpack_product_details(self, url_obj):
            unpacked_details = {}
            for key in url_obj:
                if key == "product_details":
                    for key in url_obj["product_details"]:
                            unpacked_details[key] = url_obj["product_details"][key]
                else :
                    unpacked_details[key] = url_obj[key]

            return unpacked_details


        @classmethod
        @catch_exceptions
        def clean_products(self, base_url=None, url_obj={}, soup=None, spec={},browser=False):
            
            self.clean_return_functions = {
                "string" : self.clean_str,
                "list" : self.clean_list,
                "json" : self.clean_json,
                "integer" : self.clean_integer
            }
            unpacked_obj = {}
            cleaned_obj = {}
            default_0 = ["store_overall_rating", "listing_price", "no_of_answered", "product_price", "product_rating", "store_overall_rating", "rating", "total_review_count", "reviews", "saved_price", "shipping_price", "store_rating"]
            
            if isinstance(url_obj, dict) and (self.validate(url_obj, spec) or spec["type"] == "clean_best_sellers") :
                unpacked_obj = self.unpack_product_details(url_obj)
                for key in spec["keys"]:
                    cleaned_obj[key] = self.clean_return_functions[spec["keys"][key]["return_type"]](unpacked_obj.get(spec["keys"][key]["target"], ""), key, spec)
                    if key == "brand" and cleaned_obj["brand"] == "not_available":
                        cleaned_obj[key] = self.clean_return_functions[spec["keys"][key]["return_type"]](unpacked_obj.get("brand_image", ""), key, spec)

                    if key in default_0 and cleaned_obj[key] == "not_available":
                        cleaned_obj[key] = "0" 
                
                self.split_hierarchy(cleaned_obj)
                if spec["type"] != "clean_best_sellers":
                    self.split_images(spec, cleaned_obj, "images", "image_{}")
                    self.change_key_value(cleaned_obj, "specifications")
                    if cleaned_obj.get("marketplace_id", "") == "":
                        return {}

                    if cleaned_obj["description"] == "not_available":
                        cleaned_obj["description"] = ""
                    else :
                        cleaned_obj["description"] += '\n'

                    if cleaned_obj["description_list"] != ["not_available"]:
                        cleaned_obj["description"] += '\n'.join(cleaned_obj["description_list"])
                    cleaned_obj["description_list"] = '\n'.join(cleaned_obj["description_list"])
                    cleaned_obj["highlights"] = '\n'.join(cleaned_obj["highlights"])
                else:
                    self.split_images(spec, cleaned_obj, "images", "product_image_{}")        

                cleaned_obj["type"] = spec["next_type"]
                return cleaned_obj
            else:
                 return {}

        @classmethod
        @catch_exceptions
        def clean_reviews(self, base_url, url_obj, soup, spec,browser=False):
            self.clean_return_functions = {
                "string" : self.clean_str,
                "list" : self.clean_list,
                "json" : self.clean_json,
                "integer" : self.clean_integer
            }
            review_objects = []
            if isinstance(url_obj, dict):
                unpacked_obj = self.unpack_product_details(url_obj)
                for key in spec["keys"]:
                    # self.clean_return_functions[spec["keys"][key]](unpacked_obj.get(key,""), spec)
                    unpacked_obj[key] = self.clean_return_functions[spec["keys"][key]["return_type"]](unpacked_obj.get(spec["keys"][key]["target"],""), key, spec)
               
                self.split_hierarchy(unpacked_obj)
                self.change_key_value(unpacked_obj, "rating_details")
                review_obj_template = {}
                
                for each_review in unpacked_obj["page_reviews"]:
                    review_obj = review_obj_template.copy()
                    for key in each_review:
                        if key == "review_date":
                            review_obj[key] = self.clean_date(each_review[key], spec)
                        else:
                            review_obj[key] = each_review[key]
                    self.split_images(spec, review_obj, "review_description_images", "review_image_{}")

                    review_obj["rid"] = str(uuid.uuid4())
                    review_obj["type"] = spec["next_type"]
                    review_objects.append(review_obj)
                return review_objects
        
        @classmethod
        @catch_exceptions
        def clean_date(self, date, spec):
            if date == "not available":
                return date
            dat = date.replace(',',' ').replace('/',' ')
            current_time = datetime.now()
            
            if spec["marketplace"] == "Flipkart":
                if dat.find("day") != -1:
                    dat = int(dat.split()[0])
                    dat = current_time - timedelta(days=dat)
                else:
                    if(len(dat.split())<3):
                        dat = "1 "+dat
                    dat = datetime.strptime(dat,"%d %b %Y")
            elif spec["marketplace"] == "eBay":
                dat = datetime.strptime(dat,"%b %d %Y")
            elif spec["marketplace"] == "Amazon In":
                dat = datetime.strptime(dat,"%d %B %Y")
            elif spec["marketplace"] == "Amazon USA":
                dat = datetime.strptime(dat,"%B %d %Y")
            elif spec["marketplace"] == "Bonanza":
                dat = datetime.strptime(dat,"%m %d %y")
            return str(dat)   

        @classmethod
        @catch_exceptions
        def validate(self, url_obj, spec):
            
            description = url_obj["product_details"].get("description","")
            description_list = url_obj["product_details"].get("description_list","")
            title = url_obj["product_details"].get("product_title","")
            if (description == "" or description_list == "") and title == "":
                return False           
            return True

        @classmethod
        @catch_exceptions
        def clean_integer(self, integer, key, spec):
            if not isinstance(integer,int):
                if "css_selector not found" in integer or integer == "" :
                    return "not_available"
            else:
                return str(integer)


        @classmethod
        @catch_exceptions
        def clean_json(self, strin, key, spec):

            if "css_selector not found" in strin or strin == "" :
                return [{}]
            else:
                if isinstance(strin, list):
                    for lis_element in strin:
                        if isinstance(lis_element, dict):
                            for key in lis_element:
                                if isinstance(lis_element[key], str):
                                    lis_element[key] = self.clean_str(lis_element[key], key, spec)
                                elif isinstance(lis_element[key], list):
                                    lis_element[key] = self.clean_list(lis_element[key], key, spec)
                return strin
        
        @classmethod
        @catch_exceptions
        def clean_str(self, uncleaned_str, key, spec):

            if not isinstance(uncleaned_str, str) or "css_selector not found" in uncleaned_str or uncleaned_str == "" :
                return "not_available"
            elif key == "images":
                return uncleaned_str
            else:
                cleaned_str = " ".join(uncleaned_str.split())
                if key in spec["keys"] and spec["keys"][key]["clean_regex"]["regex"]: 
                    if re.findall(spec["keys"][key]["clean_regex"]["regex"], cleaned_str):
                        regex_data = re.findall(spec["keys"][key]["clean_regex"]["regex"], cleaned_str)[0]        
                        for replace_with in spec["keys"][key]["clean_regex"]["replace"]:           
                            regex_data = regex_data.replace(replace_with, "")
                        return regex_data
                    
                return cleaned_str 

        @classmethod
        @catch_exceptions
        def clean_list(self, uncleaned_list, key, spec):
            if uncleaned_list == "" :
                return ["not_available"]
            if isinstance(uncleaned_list, str):
                cleaned_list = uncleaned_list.split('|')
            else:
                cleaned_list = uncleaned_list
            for i in range(len(cleaned_list)):
                cleaned_list[i] = self.clean_str(cleaned_list[i], key, spec)

            return cleaned_list