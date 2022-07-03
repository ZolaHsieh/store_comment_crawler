

import bs4
import configparser
import pandas as pd
import time
import requests
from retry import retry
from tqdm import tqdm
from sqlalchemy import create_engine, Table, Column, String, MetaData
from sqlalchemy.sql import select

config = configparser.ConfigParser()
config.read('config.ini')

url = config['foodpanda']['main_page_url']
chain_url = config['foodpanda']['chain_restaurant_url']
headers = {'accept': '*/*',
			'accept-encoding': 'gzip, deflate, br',
			'content-type': 'text/plain;charset=UTF-8',
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36',
			'x-disco-client-id':'web'
			}

db_name = config['database']['db_path']
tbl_name = config['database']['store_table']
engine = create_engine(f'sqlite:///{db_name}')

def get_city_list(web_content):
	
	# get all city url
	tmp = web_content.find_all("a",class_="city-tile")	
	all_city_link = [url+a.get("href") for a in tmp]

	# get all city title
	tmp = web_content.find_all("span" ,class_="city-name")							
	all_city_title = [(c.text).strip() for c in tmp]								

	return all_city_link, all_city_title														


def get_store_list(all_city_link, all_city_title, store, conn):
	
	for city_url, city_name in zip(all_city_link, all_city_title):
		try:
			print(city_name, city_url)
			city_tmp = pd.DataFrame()

			result = requests.get(city_url, headers=headers)
			if result.status_code!=200: raise ValueError(f"Fail to get {city_name} main page")
			print(f'get {city_name} page: ',result)

			web_content = bs4.BeautifulSoup(result.content , "html.parser")	
			vendor_list_li = web_content.find_all('ul', class_='vendor-list')[0]
			
			# store_name_list
			tmp = vendor_list_li.find_all("span", class_="name fn")
			store_list = [(c.text).strip() for c in tmp]
			print('store_list:', len(store_list))

			# store rating
			tmp = vendor_list_li.find_all("span", class_="rating")
			rating = [(c.text).strip() for c in tmp]
			print('rating:', len(rating))

			# get store menu url
			tmp = vendor_list_li.find_all("a", class_="hreview-aggregate url")
			store_url = [(b.get('href')) for b in tmp]
			print('store_url:', len(store_url))

			# data processed
			city_tmp['store']=store_list
			city_tmp['rating']=rating
			city_tmp['store_url']=store_url
			tmp = city_tmp['store_url'].str.split('/',expand=True)
			city_tmp['store_id']=tmp[tmp.shape[1]-2]
			city_tmp['city_name']=city_name
			city_tmp['city_url']=city_url
			city_tmp['chk']= ''
			print('data shape:',city_tmp.shape)

			# update len(store_id) > 4
			print('====== update ======')
			update_tmp = city_tmp[city_tmp['store_id'].str.len()!=4].reset_index(drop=True)
			print(update_tmp.shape)

			if ~update_tmp.empty: 
				update_tmp = update_store_id(update_tmp)
				city_tmp = city_tmp[city_tmp['store_id'].str.len()==4]
				city_tmp = pd.concat([city_tmp, update_tmp], axis=0).reset_index(drop=True)
			print('update store id:',update_tmp.shape, city_tmp.shape)
			
			# filtered existed store
			print('===== filtered ====== ')
			s = select([store]).where(store.c.store.in_(store_list)&(store.c.city_name==city_name))
			result = conn.execute(s)

			db_tmp = pd.DataFrame(result)
			if ~db_tmp.empty:
				db_tmp.columns = result.keys()
				print('store data in db:',db_tmp.shape)
				city_tmp = pd.concat([city_tmp, db_tmp], axis=0).drop_duplicates(subset=['store','city_name','store_id','store_url'], keep=False, ignore_index=True)
			
			city_tmp = city_tmp[city_tmp.chk==''].reset_index(drop=True)
			print('filtered shape:',city_tmp.shape)
			
			# insert store list
			if ~city_tmp.empty: city_tmp.to_sql(tbl_name, con=engine, if_exists='append', index=False)
				
			time.sleep(3)
			# break
		except Exception as e:
			print(e)
			# break
			continue
	return


def tbl_check():
	meta = MetaData()
	store = Table(f'{tbl_name}', meta, 
		Column('store', String, primary_key=True), 
		Column('rating', String), 
		Column('store_url', String, primary_key=True),
		Column('store_id', String, primary_key=True), 
		Column('city_name', String, primary_key=True),
		Column('city_url', String),
		Column('chk', String))
	meta.create_all(engine)
	return store


def update_store_id(store_data):

	for _, rows in tqdm(store_data.iterrows()):
		# store menu url
		query_url = chain_url.format(rows['store_id'])
		
		try:
			# get store menu by api
			r = requests.get(url=query_url, headers=headers) 
			if r.status_code == requests.codes.ok:
				data = r.json()
				store_id = data["data"]["items"][0]["code"]
				web_url = data["data"]["items"][0]['redirection_url']
				
				# stmt=store.update().where(store.c.store_id==rows['store_id']).values(store_id=store_id, store_url=web_url)
				# conn.execute(stmt)
				store_data.loc[store_data.store==rows['store'],['store_id']] = store_id
				store_data.loc[store_data.store==rows['store'],['store_url']] = web_url
				
				time.sleep(1)
                # break
			else: raise Exception('請求失敗 ' + str(r))
		
		except Exception as e:
			print(rows['store'], e)
			time.sleep(1)
			continue

	return store_data


@retry(Exception, delay=3, tries=5)
def main():

	# create and get tbl object
	store = tbl_check()

	result = requests.get(url, headers = headers)
	print('main page request:', result)
	try:
		if result.status_code== requests.codes.ok:
			
			web_content = bs4.BeautifulSoup(result.content , "html.parser")

			# get all city restaurant url
			all_city_link, all_city_title = get_city_list(web_content) 

			# get store list
			conn = engine.connect()
			get_store_list(all_city_link, all_city_title, store, conn)
			print('get store list finished!')

		else: 
			print('query error!')
			raise Exception
			
	except Exception as e:
		print(e)

	finally: 
		conn.close()
	


if __name__ == "__main__":
	main()