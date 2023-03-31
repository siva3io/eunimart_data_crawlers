'''
this program is to extract the seed urls of the best sellers products of Amazon USA
'''
from bs4 import BeautifulSoup
import requests

class HierarchyBestSeller(object):

    
        debugger = None 

        def __init__(self):
           pass

    
        @classmethod
        def find_best_seller(self, url, marketplace):
            
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            first_level_soup = soup.select("ul#zg_browseRoot > ul > li > a")
            # print(first_level_soup)

            first_level_links = [] 
            first_level_names = []
            for each_a_tag in first_level_soup:
                first_level_names.append( each_a_tag.text )
                first_level_links.append( each_a_tag.get("href") )
            
            
            second_level_names = []
            second_level_links = [] 
            
            for index  in range(0,len(first_level_links)):
                response = requests.get(first_level_links[index])
                soup = BeautifulSoup(response.text, 'html.parser')
                second_level_soup = soup.select("ul#zg_browseRoot > ul > ul > li > a")
                for each_a_tag in second_level_soup:
                    second_level_names.append( first_level_names[index]+"|"+each_a_tag.text )
                    second_level_links.append( each_a_tag.get("href") )

            for i in range(len(second_level_links)):
                with open ("seed_urls_best_seller_AmazonIN.json","a+") as f:
                    f.write('{ "hierarchy": ' + '"' + second_level_names[i] + '"' + ', "url": ' + '"' + second_level_links[i] + '"' + ', "type":  "best_seller",' + '"marketplace": ' + '"' + marketplace + '"' + ' },'+'\n')
                

#"https://www.amazon.com/Best-Sellers/zgbs/ref=zg_bs_unv_pc_0_3015433011_4"
# "https://www.amazon.in/gp/bestsellers/ref=zg_bs_unv_MI_0_4654565031_4"
seller = HierarchyBestSeller()

seller.find_best_seller("https://www.amazon.in/gp/bestsellers/ref=zg_bs_unv_MI_0_4654565031_4", "Amazon India")