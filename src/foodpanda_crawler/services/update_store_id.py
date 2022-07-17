import pandas as pd
import requests
from sqlalchemy import create_engine, Table, Column, String, MetaData
from sqlalchemy.sql import select, func
import time
import json


# db info
db_name = 'foodpanda_store_info.db'
store_tbl = 'foodpanda_store_list'

engine = create_engine(f'sqlite:///{db_name}')
conn = engine.connect()

chain_url = 'https://disco.deliveryhero.io/listing/api/v1/pandora/chain?chain_code={}&include=metadata&country=tw'
header = {
    'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
    'x-disco-client-id':'web'}

def update_store(store, store_data):
    
    for rows in store_data:
        # store menu url
        url = chain_url.format(rows['store_id'])
        print(rows['store'], url)
        print(rows)
        try: 
            # get store menu by api
            r = requests.get(url=url, headers=header) 
            if r.status_code == requests.codes.ok:
                data = r.json()
                stoe_id = data["data"]["items"][0]["code"]
                web_url = data["data"]["items"][0]['redirection_url']
                # print(stoe_id, web_url)

                stmt=store.update().where(store.c.store_id==rows['store_id']).values(store_id=stoe_id, store_url=web_url)
                conn.execute(stmt)

                time.sleep(2)
                # break
            else: 
                print('請求失敗', r)
                raise Exception('請求失敗 ' + str(r))

        except Exception as e:
            print(rows['store'], e)
            time.sleep(2)
            # break
            continue

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
    
    return store

def get_store_list(store):
    stmt = select([store]).where((func.length(store.c.store_id) > 4))
    result = conn.execute(stmt)
    return result


def main():

    store = get_tbl()
    result = get_store_list(store)
    update_store(store, result)



if __name__ == "__main__":
    main()
    conn.close()