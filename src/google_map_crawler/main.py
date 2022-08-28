from tqdm import tqdm
from src import logging_, store_reviews_db
from src.db_conn.models import GStore, FStore
from src.google_map_crawler.services.google_store_crawler import GoogleStoreCrawler
from src.google_map_crawler.services.google_review_crawler import GoogleReviewCrawler

logger = logging_.getLogger(__name__)

def crawler():
    logger.info('Start job.')

    # Store
    # f_stores = store_reviews_db.select_store(FStore, '肉')
    f_stores = store_reviews_db.select_checked_store(FStore)
    for f_store in tqdm(f_stores):
        search_context = f'{f_store.city_name} {f_store.store}'
        g_review_crawler = GoogleStoreCrawler(delay=5, logger=logger)
        g_store = g_review_crawler.run(search_context=search_context, f_store_id=f_store.store_id)
        print(g_store)
        store_reviews_db.insert_all([g_store])

    # Reviews
    g_stores = store_reviews_db.select_checked_store(GStore)
    for g_store in tqdm(g_stores):
        google_reviews_crawler = GoogleReviewCrawler(store_id=g_store.f_store_id, 
                                                    reviews_url=g_store.reviews_url, 
                                                    reviews_count=g_store.reviews_count, 
                                                    delay=0, logger=logger)
        store_reviews = google_reviews_crawler.run()
        store_reviews_db.insert_all(store_reviews)

    store_reviews_db.engine_dispose()
    logger.info('End job.')
