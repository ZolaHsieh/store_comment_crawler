
import time
import logging

from tqdm import tqdm
from common.setup_logger import logger
from db_conn.db_conn import StoreReviewsDB
from db_conn.models import Base
from services.foodpanda_store_info_crawler import FoodpandaCrawler #get_store_list, get_store_list, update_store_id



if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.info('Start job.')
    db_conn_info = 'sqlite:///../db/foodpanda_store_info.db?charset=utf8'
    store_reviews_db = StoreReviewsDB(base=Base, info=db_conn_info)
    foodpanda_crawler = FoodpandaCrawler(db_obj=store_reviews_db)
    
    ## get city list
    logger.info('Start crawling city list.')
    all_city_link, all_city_title = foodpanda_crawler.get_all_city_url()
    logger.info('End crawling city list.')

    ## get store list
    logger.info('Start crawling store list of each city.')
    for city_url, city_name in zip(all_city_link, all_city_title):
        logger.info(f'{city_name}:{city_url}')
        try:
            foodpanda_crawler.get_all_stores_of_city(city_name, city_url)
        except Exception as e:
            logger.error(e)
            continue

    logger.info('End store list of each city.')

    store_reviews_db.engine_dispose()
    logger.info('End job.')