from src import logging_, args, store_reviews_db
from .services.foodpanda_store_info_crawler import FoodpandaCrawler
from .services import foodpanda_info_postprocessed

logger = logging_.getLogger(__name__)

def run_fd_crawler(store=True, update_chain=True, menu=True, post_processed=False):
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
                # if city_name !='台中市':continue
                logger.info(f'{city_name}:{city_url}')
                try:
                    foodpanda_crawler.get_all_stores_of_city(city_name, city_url)
                except Exception as e:
                    logger.error(e)
                    continue
                
            logger.info('End store list of each city.')

        if update_chain:
            logger.info('Start update chain stores.')
            foodpanda_crawler.update_chain_store_id(update_db=True)
            logger.info('End update chain stores.')

        if menu:
            logger.info('Start crawling menus of stores.')
            foodpanda_crawler.get_menu()      
            logger.info('End crawling menus of stores.')

        if post_processed:
            logger.info('Start post processed of stores.')
            foodpanda_info_postprocessed.f_store_info_post_processed(store_reviews_db)      
            logger.info('End cpost processed of stores.')
    
    except Exception as e:
        logger.info('Run job Error:' + str(e))

    finally:
        store_reviews_db.engine_dispose()
        logger.info('End run_fd_crawler job.')


if __name__ == '__main__':
    logger.info('Start job.')
    try:
        run_fd_crawler(args.store, args.update_chain, args.menu, args.post_processed)
    except Exception as e:
        logger.error(e)
    finally:
        store_reviews_db.engine_dispose()
        logger.info('End job.')