import bs4
import pandas as pd
import requests
import time

from tqdm import tqdm
from db_conn.models import FStore, FStoreMenu, FStoreSchedule

class FoodpandaCrawler():
    def __init__(self, db_obj):
        self.db_obj = db_obj

        self.main_page_url = 'https://www.foodpanda.com.tw'
        self.chain_url = 'https://disco.deliveryhero.io/listing/api/v1/pandora/chain?chain_code={}&include=metadata&country=tw'
        self.menu_api = 'https://tw.fd-api.com/api/v5/vendors/{}'
        self.headers = {'accept': '*/*',
                        'accept-encoding': 'gzip, deflate, br',
                        'content-type': 'text/plain;charset=UTF-8',
                        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36',
                        'x-disco-client-id':'web'}

        self.menu_params = {'include': 'menus',
                            'language_id': '6',
                            'basket_currency': 'TWD',
                            'opening_type': 'delivery'}

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
          
            # insert store list
            if not store_data.empty: self.db_obj.insert_store_df(FStore, store_data)
            time.sleep(2)

        except Exception as e:
            print(e)

    def get_menu(self):
        store_data = self.db_obj.select_uncheck_store(FStore)
        for rows in store_data:
            # print(rows)
            if rows.store_id=='': continue

            url = self.menu_api.format(rows.store_id)
            try:
                # get store menu by api
                r = requests.get(url=url, params=self.menu_params) 
                if r.status_code == requests.codes.ok:
                    data = r.json()
                    print('店名:', data['data']['name'])
                    print('地址:', data['data']['address'])
                    print('(lon, lat):', data['data']['longitude'], data['data']['latitude']) # latitude longitude

                    ## insert menus
                    if data['data']['menus'] != None: 
                        menu_list=pd.DataFrame()
                        menu_list = self.__menu_data_processed(data['data']['menus'][0])
                        menu_list['menu_url'] = url
                        menu_list['store_id'] = rows.store_id
                        if not menu_list.empty: self.db_obj.insert_menu_df(FStoreMenu, menu_list)

                    # insert schedules
                    if data['data']['schedules'] != None: 
                        tmp_s = pd.json_normalize(data['data']['schedules'])
                        tmp_s['store_name'] = rows.store_name
                        col = ['store_name','id','weekday','opening_type','opening_time','closing_time']
                        for c in col: 
                            if c not in list(tmp_s.columns): tmp_s[c] = ''
                            tmp_s[c] = tmp_s[c].astype(str)
                        tmp_s = tmp_s.rename(index=str, columns={'id':'store_id'})
                        if not tmp_s.empty: self.db_obj.insert_schedule_df(FStoreSchedule, tmp_s)

                    # update store tbl
                    update_dict = {
                        'city_name':rows.city_name,
                        'store_id':rows.store_id,
                        'store_name':rows.store_name,
                        'address': data['data']['address'],
                        'longitude': data['data']['longitude'],
                        'latitude': data['data']['latitude']}
                    self.db_obj.update_store_df(FStore, update_dict)                        

                    break
                    time.sleep(2)
                else: 
                    print('請求失敗', r)
                    raise Exception('請求失敗 ' + str(r))

            except Exception as e:
                print(rows.store_name, e)
                time.sleep(2)
                break

    def update_store_id(self):
        
        chain_store = self.db_obj.select_chain_store(FStore)
        for row in chain_store:
            print(row)
            break

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

    def __menu_data_processed(self, data):
        menu_list = pd.DataFrame()
        for item in data['menu_categories']: 
            if item['name']=='※注意事項': continue
            
            category = item['name']
            tmp_m = pd.json_normalize(item['products'])
            col = ['menu_url', 'id', 'code', 'name',
                'description', 'display_price', 'master_category_id', 'category','tags']
            for c in col: 
                if c not in list(tmp_m.columns): tmp_m[c] = ''
                tmp_m[c] = tmp_m[c].astype(str)
            tmp_m['category'] = category
            
            tmp_m = tmp_m[col].rename(index=str, columns={'id':'dishes_id','code':'dishes_code','name':'dishes_name'})
            menu_list = pd.concat([menu_list, tmp_m], axis=0).reset_index(drop=True)
        
        return menu_list