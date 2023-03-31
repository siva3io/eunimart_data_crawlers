import json
import os
import gzip

def return_json_files(files, path):
    FILE_PATH = path
    for f in files:
        if os.path.isfile(os.path.join(FILE_PATH,f)):
            with gzip.open(os.path.join(FILE_PATH,f), 'rb') as product:
                product_dic = json.loads(product.read())
                if "product_title" in product_dic["product_details"].keys():
                    product_dic["type"] = "clean_data"
                    product_dic["file_path"] = f                                        
                    yield product_dic   
