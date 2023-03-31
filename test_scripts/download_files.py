
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from parsers.util import Utils,catch_exceptions

CURRENT_WORKING_DIRECTORY = os.getcwd()

with open(os.path.join(CURRENT_WORKING_DIRECTORY, "../specs.json")) as json_file:
    spec_dic = json.load(json_file)


Utils.download_folder_s3(spec_dic['Flipkart']['review_info'])

print("completed")




