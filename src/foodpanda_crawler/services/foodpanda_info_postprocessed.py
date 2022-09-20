from src import logging_, store_reviews_db
from src.db_conn.models import FStore, FStoreProcessed
from tqdm import tqdm
import re

logger = logging_.getLogger(__name__)

def f_store_info_post_processed(db_obj):

    logger.info('Start f_store_info_post_processed.')
    try:
        city_list = ['台北市','新北市','桃園市','台中市','台南市','高雄市','新竹縣','苗栗縣','彰化縣','南投縣','雲林縣','嘉義縣','屏東縣',
                        '宜蘭縣','花蓮縣','台東縣','澎湖縣','金門縣','連江縣','新竹市','嘉義市']
        # get rawdata from db
        stores = db_obj.select_f_store_addr_to_update(FStore, FStoreProcessed)
        
        # post processed
        for s in tqdm(stores):
            logger.info(f"{s.city_name}, {s.store_id}, {s.store_name}, {s.address}")

            processed_result = FStoreProcessed()
            processed_result.city_name = s.city_name
            processed_result.store_id = s.store_id
            processed_result.chain_id = s.chain_id
            processed_result.store_name = s.store_name
            processed_result.rating = s.rating
            processed_result.address = s.address

            new_addr = re.sub(r"\A([(]\S[)])+", "", s.address.replace(' ',''), 2)
            # print('~~~',new_addr)
            if new_addr:
                processed_result.address = new_addr
                new_city = re.match('|'.join(city_list), new_addr.replace('臺','台'))
                if new_city: processed_result.new_city_name = new_city.group(0)

                # upsert
                db_obj.upsert_f_post_stores(FStoreProcessed, processed_result)
            # break
    except Exception as e:
            logger.info('Run job Error:' + str(e))

    finally:
        store_reviews_db.engine_dispose()
        logger.info('End f_store_info_post_processed.')

if __name__ == '__main__':
    logger.info('Start job.')
    try:
        f_store_info_post_processed(store_reviews_db)
    except Exception as e:
        logger.error(e)
    finally:
        store_reviews_db.engine_dispose()
        logger.info('End job.')