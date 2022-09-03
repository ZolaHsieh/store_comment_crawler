from tqdm import tqdm
from src import logging_, store_reviews_db, args
from src.db_conn.models import GStore, FStore, GStoreReview
from src.google_map_crawler.services.google_store_crawler import GoogleStoreCrawler
from src.google_map_crawler.services.google_review_crawler import GoogleReviewCrawler

logger = logging_.getLogger(__name__)

def run_gm_crawler():
    logger.info('Start google_map_crawler job.')
    try:
        # Store
        f_stores = store_reviews_db.select_f_store_to_update(FStore, GStore, args.exist_g_update)
        for f_store in tqdm(f_stores):
            g_review_crawler = GoogleStoreCrawler(delay=5, logger=logger)
            g_store, suc_bool = g_review_crawler.run(f_store=f_store)

            if suc_bool:
                logger.info(f'Update google store for {g_store}')
                store_reviews_db.upsert_g_store(GStore, g_store)
                
        # Reviews
        g_stores = store_reviews_db.select_uncheck_store(GStore)
        for g_store in tqdm(g_stores):
            if not g_store.reviews_url:
                Exception('No google store reviews_url')
            google_reviews_crawler = GoogleReviewCrawler(g_store=g_store,
                                                        delay=0, logger=logger)
            store_reviews = google_reviews_crawler.run()
            logger.info(f'Update google reviews for {g_store}')
            store_reviews_db.delsert_g_reviews(GStoreReview, store_reviews)
            g_store.chk = True
            store_reviews_db.upsert_g_store(GStore, g_store)
            
    except Exception as exec:
        logger.error(str(exec))
    finally:
        store_reviews_db.engine_dispose()
    logger.info('End google_map_crawler job.')
