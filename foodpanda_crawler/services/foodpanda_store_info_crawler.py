import bs4
import pandas as pd
import requests
import time

from tqdm import tqdm
from db_conn.models import FStore

class FoodpandaCrawler():
    def __init__(self, db_obj):
        self.db_obj = db_obj

        self.main_page_url = 'https://www.foodpanda.com.tw'
        self.chain_url = 'https://disco.deliveryhero.io/listing/api/v1/pandora/chain?chain_code={}&include=metadata&country=tw'
        self.headers = {'accept': '*/*',
			'accept-encoding': 'gzip, deflate, br',
			'content-type': 'text/plain;charset=UTF-8',
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36',
			'x-disco-client-id':'web'
			}

    def get_all_city_url(self):
        # logger.info('get_all_city_url start')

        result = requests.get(self.main_page_url, headers = self.headers)
        print('main page resuest: ',result)
        if result.status_code==200:
            web_content = bs4.BeautifulSoup(result.content , "html.parser")
            
            # get all city url
            tmp = web_content.find_all("a",class_="city-tile")	
            self.all_city_link = [self.main_page_url + a.get("href") for a in tmp]

            # get all city title
            tmp = web_content.find_all("span" ,class_="city-name")							
            self.all_city_title = [(c.text).strip() for c in tmp]								
            # print(all_city_title)	

            return self.all_city_link, self.all_city_title
        else: 
            print('query error!')
            return [],[]


    def get_all_stores_of_city(self, city_name, city_url):
        try:
            print(city_name, city_url)
            result = requests.get(city_url, headers=self.headers)
            print(result)

            web_content = bs4.BeautifulSoup(result.content , "html.parser")	
            vendor_list_li = web_content.find_all('ul', class_='vendor-list')[0]
            
            # store_name_list
            tmp = vendor_list_li.find_all("span", class_="name fn")
            store_list = [(c.text).strip() for c in tmp]
            print('store_list:', len(store_list))

            # store rating
            tmp = vendor_list_li.find_all("span", class_="rating")
            rating = [(c.text.split('/')[0]).strip() for c in tmp]
            print('rating:', len(rating))

            # get store menu url
            tmp = vendor_list_li.find_all("a", class_="hreview-aggregate url")
            store_url = [(b.get('href')) for b in tmp]
            print('store_url:', len(store_url))

            # store_data_processed
            store_data = self.__sotre_data_processed(store_list,rating, store_url, city_name, city_url)

            # filtered existed store
            print('===== filtered ====== ')
            result = self.db_obj.select_store_of_city(FStore, store_list, city_name)
            db_tmp = pd.DataFrame(result)
            print('store data in db:',db_tmp.shape)
            if not db_tmp.empty: 
                db_tmp.columns = result.keys()
                store_data = pd.concat([store_data, db_tmp], axis=0).drop_duplicates(subset=['store','city_name','store_id','chain_id','store_url'], keep=False, ignore_index=True)
                store_data = store_data[store_data.chk==False].reset_index(drop=True)
                print('filtered shape:',store_data.shape)
            
            # insert store list
            if not store_data.empty: self.db_obj.insert_store_df(FStore, store_data)
            time.sleep(3)

        except Exception as e:
            print(e)


    def __sotre_data_processed(self, store_list,rating, store_url, city_name, city_url):
        
        processed_data = pd.DataFrame()
        # data processed
        processed_data['store_name']=store_list
        processed_data['rating']=rating
        processed_data['store_url']=store_url
        processed_data['city_name']=city_name
        processed_data['city_url']=city_url
        processed_data['chk']= False

        # store_id/chain id
        tmp = processed_data['store_url'].str.split('/',expand=True)
        chain_id_list=[]
        sotre_id_list=[]
        for t in list(tmp[tmp.shape[1]-2]):
            if len(t)==4:
                sotre_id_list.append(t)
                chain_id_list.append('')
            else:
                sotre_id_list.append('')
                chain_id_list.append(t)

        processed_data['store_id']=sotre_id_list
        processed_data['chain_id']=chain_id_list
        
        print('processed data shape:',processed_data.shape)
        return processed_data
