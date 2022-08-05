import argparse
import logging

# from src.common.setup_logger import logger
from src.db_conn.db_conn import StoreReviewsDB
from src.db_conn.models import Base
from .services.foodpanda_store_info_crawler import FoodpandaCrawler #get_store_list, get_store_list, update_store_id



if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.info('Start job.')

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--store', action="store_true")
    parser.add_argument('-m', '--menu', action="store_true")
    parser.add_argument('-uc', '--update_chain', action="store_true")
    args = parser.parse_args()

    db_conn_info = 'sqlite:///./db/foodpanda_store_info.db?charset=utf8'
    store_reviews_db = StoreReviewsDB(base=Base, info=db_conn_info)
    foodpanda_crawler = FoodpandaCrawler(db_obj=store_reviews_db)
    
    if args.store:
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
                break
            except Exception as e:
                logger.error(e)
                break
                continue
        logger.info('End store list of each city.')
    
    if args.menu:
      logger.info('Start crawling menus of stores.')
      foodpanda_crawler.get_menu()      
      logger.info('End crawling menus of stores.')

    if args.update_chain:
        logger.info('Start update chain stores.')
        foodpanda_crawler.update_chain_store_id()
        logger.info('End update chain stores.')


    store_reviews_db.engine_dispose()
    logger.info('End job.')