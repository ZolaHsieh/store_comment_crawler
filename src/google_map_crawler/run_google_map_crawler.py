from tqdm import tqdm
from src import logging_, store_reviews_db
from src.db_conn.models import GStore, FStore
from src.google_map_crawler.services.google_store_crawler import GoogleStoreCrawler
from src.google_map_crawler.services.google_review_crawler import GoogleReviewCrawler

logger = logging_.getLogger(__name__)

def run_gm_crawler():
    logger.info('Start google_map_crawler job.')

    # Store
    # f_stores = store_reviews_db.select_store(FStore, '肉')
    f_stores = store_reviews_db.select_uncheck_store(FStore, GStore)
    for f_store in tqdm(f_stores):
        search_context = f'{f_store.city_name} {f_store.store_name} {f_store.store_name}'
        g_review_crawler = GoogleStoreCrawler(delay=5, logger=logger)
        g_store, suc_bool = g_review_crawler.run(search_context=search_context, f_store=f_store)
        
        if suc_bool:
            print(g_store)
            store_reviews_db.insert([g_store])

    # Reviews
    g_stores = store_reviews_db.select_check_store(GStore)
    for g_store in tqdm(g_stores):
        google_reviews_crawler = GoogleReviewCrawler(g_store=g_store,
                                                    delay=0, logger=logger)
        store_reviews = google_reviews_crawler.run()
        store_reviews_db.insert(store_reviews)

    store_reviews_db.engine_dispose()
    logger.info('End google_map_crawler job.')
