import argparse
from src import logging_, store_reviews_db
from .services.foodpanda_store_info_crawler import FoodpandaCrawler

logger = logging_.getLogger(__name__)

def run_fd_crawler(store=True, update_chain=True, menu=True):
    logger.info('Start run_fd_crawler job.')
    try:
        foodpanda_crawler = FoodpandaCrawler(db_obj=store_reviews_db)

        if store:
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

        if update_chain:
            logger.info('Start update chain stores.')
            foodpanda_crawler.update_chain_store_id()
            logger.info('End update chain stores.')

        if menu:
            logger.info('Start crawling menus of stores.')
            foodpanda_crawler.get_menu()      
            logger.info('End crawling menus of stores.')
    
    except Exception as e:
        logger.info('Run job Error:' + str(e))

    finally:
        store_reviews_db.engine_dispose()
        logger.info('End run_fd_crawler job.')

if __name__ == '__main__':
    logger.info('Start job.')

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--store', action="store_true")
    parser.add_argument('-m', '--menu', action="store_true")
    parser.add_argument('-uc', '--update_chain', action="store_true")
    args = parser.parse_args()

    run_fd_crawler(args.store, args.update_chain, args.menu)
    store_reviews_db.engine_dispose()
    logger.info('End job.')