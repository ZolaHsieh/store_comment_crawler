import configparser
import pandas as pd
import requests
from sqlalchemy import create_engine, Table, Column, String, MetaData
from sqlalchemy.sql import select, func
import time
import json

config = configparser.ConfigParser()
config.read('config.ini')

api_url = config['foodpanda']['menu_api']
params = {
    'include': 'menus',
    'language_id': '6',
    'basket_currency': 'TWD',
    'opening_type': 'delivery',
}

# db info
db_name = config['database']['db_path']
store_tbl = config['database']['store_table']
menu_tbl = config['database']['menu_table']
schedule_tbl = config['database']['schedule_table']
engine = create_engine(f'sqlite:///{db_name}')

def get_store_menu(store_data, store, menu, schedule, conn):
    
    menu_list=pd.DataFrame()
    schedule_list=pd.DataFrame()
    for rows in store_data:
        # store menu url
        url = api_url.format(rows['store_id'])
        print(rows['store'], url)
        try:
            # get store menu by api
            r = requests.get(url=url, params=params) 
            if r.status_code == requests.codes.ok:
                data = r.json()
                print('店名:', data['data']['name'])
                print('地址:', data['data']['address'])
                print('(lon, lat):', data['data']['longitude'], data['data']['latitude']) # latitude longitude

                # menus
                if data['data']['menus'] == None: continue
                
                tmp = data['data']['menus'][0]
                tmp_menu=pd.DataFrame()
                for item in tmp['menu_categories']: 
                    if item['name']=='※注意事項': continue
                    
                    category = item['name']
                    tmp_m = pd.json_normalize(item['products'])
                    tmp_m['category'] = category
                    tmp_m['menu_url'] = url

                    tmp_m['store_name'] = rows['store']
                    tmp_m['store_name_1'] = data['data']['name']
                    tmp_m['address'] = data['data']['address']
                    tmp_m['longitude'] = data['data']['longitude']
                    tmp_m['latitude'] = data['data']['latitude']
                    # tmp_m['description'] = ''
                    tmp_menu = pd.concat([tmp_menu, tmp_m], axis=0).reset_index(drop=True)
                    
                #insert tmp_menu to menu tbl
                col = ['store_name', 'address', 'longitude','latitude', 'menu_url', 'id', 'code','name', 
                        'description', 'display_price', 'master_category_id', 'category','tags']
                for c in col: 
                    if c not in list(tmp_menu.columns): tmp_menu[c] = 'NA'
                    tmp_menu[c] = tmp_menu[c].astype(str)
                
                s = json.loads(tmp_menu[col].to_json(orient="records"))
                conn.execute(menu.insert(), s)
                
                menu_list = pd.concat([menu_list, tmp_menu], axis=0).reset_index(drop=True)
                print('menu: ',menu_list.shape, tmp_menu.shape)

                # schedules
                tmp_s = pd.json_normalize(data['data']['schedules'])
                tmp_s['store_name'] = rows['store']

                #insert schedule tbl
                col = ['store_name','id','weekday','opening_type','opening_time','closing_time']
                for c in col: 
                    if c not in list(tmp_s.columns):  tmp_s[c] = 'NA'
                    tmp_s[c] = tmp_s[c].astype(str)

                s = json.loads(tmp_s[col].to_json(orient="records"))
                conn.execute(schedule.insert(), s)

                schedule_list = pd.concat([schedule_list, tmp_s], axis=0).reset_index(drop=True)
                print('schedule: ',schedule_list.shape, tmp_s.shape)
                
                #update store tbl
                stmt=store.update().where(store.c.store_id==rows['store_id']).values(chk='Y')
                conn.execute(stmt)

                # break
                time.sleep(2)
            else: 
                print('請求失敗', r)
                raise Exception('請求失敗 ' + str(r))

        except Exception as e:
            print(rows['store'], e)
            time.sleep(2)
        
    return schedule_list, menu_list


def get_tbl():
    meta = MetaData()
    store = Table(f'{store_tbl}', meta, 
        Column('store', String, primary_key=True), 
		Column('rating', String), 
		Column('store_url', String, primary_key=True),
		Column('store_id', String, primary_key=True), 
		Column('city_name', String, primary_key=True),
		Column('city_url', String),
		Column('chk', String))

    menu = Table(f'{menu_tbl}', meta,
        Column('store_name', String),
        Column('address', String),
        Column('longitude', String),
        Column('latitude', String), 
        Column('menu_url', String),
		Column('id', String), 
		Column('code', String),
		Column('name', String),
		Column('description', String),
		Column('display_price', String),
		Column('master_category_id', String),
        Column('category', String),
        Column('tags', String))

    schedule = Table(f'{schedule_tbl}', meta, 
		Column('store_name', String), 
		Column('id', String), 
		Column('weekday', String),
		Column('opening_type', String), 
        Column('opening_time', String), 
		Column('closing_time', String))

    meta.create_all(engine)
    return store, menu, schedule


def get_store_list(store, conn):

    conn = engine.connect()
    stmt = select([store]).where((func.length(store.c.store_id) == 4)&(store.c.chk==''))
    result = conn.execute(stmt)

    return result


def main():

    # check & create schedule & menu tbl
    store, menu, schedule = get_tbl()
    try:
        conn = engine.connect()

        # get data from store tbl
        store_data = get_store_list(store, conn)

        # get store menu / schedule
        schedule_list, menu_list = get_store_menu(store_data, store, menu, schedule, conn)

        # schedule_list.to_csv('data/all_stores_schedule.csv', index=False)
        # menu_list.to_csv('data/all_stores_menu.csv', index=False)
    except Exception as e: 
        print('error:', str(e))

    finally: 
        conn.close()

    print('finished crawling & parsing!!')


if __name__ == "__main__":
    main()