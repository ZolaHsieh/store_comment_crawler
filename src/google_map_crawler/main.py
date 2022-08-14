from tqdm import tqdm
import logging
# import time
import os

from src.db_conn.db_conn import StoreReviewsDB
from src.db_conn.models import Base, GStore, FStore
from .services.google_store_crawler import GoogleStoreCrawler
from .services.google_review_crawler import GoogleReviewCrawler

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(name)s][%(levelname)5s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


logger = logging.getLogger(__name__)
logger.info('Start job.')

db_conn_info = 'mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8'.format(user=os.getenv('MYSQL_USER'),
                                                                    password=os.getenv('MYSQL_PASSWORD'),
                                                                    host='db',
                                                                    port=3306,
                                                                    database=os.getenv('MYSQL_DATABASE'))
                                                            
store_reviews_db = StoreReviewsDB(base=Base, info=db_conn_info)

# Store
# f_stores = store_reviews_db.select_store_name(FStore, '肉')
# f_stores = store_reviews_db.get_checked_store(FStore)
# for f_store in tqdm(f_stores):
#     search_context = f'{f_store.city_name} {f_store.store}'
#     g_review_crawler = GoogleStoreCrawler(delay=5, logger=logger)
#     g_store = g_review_crawler.run(search_context=search_context, f_store_id=f_store.store_id)
#     print(g_store)
#     store_reviews_db.insert_all([g_store])

# # Reviews
# g_stores = store_reviews_db.get_checked_store(GStore)
# for g_store in tqdm(g_stores):
#     google_reviews_crawler = GoogleReviewCrawler(store_id=g_store.f_store_id, reviews_url=g_store.reviews_url, reviews_count=g_store.reviews_count, delay=0, logger=logger)
#     store_reviews = google_reviews_crawler.run()
#     store_reviews_db.insert_all(store_reviews)

store_reviews_db.engine_dispose()
logger.info('End job.')
