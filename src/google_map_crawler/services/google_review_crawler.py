import re
from pkg_resources import yield_lines
import requests
import json
import logging
import time
import sys
from dataclasses import dataclass
from tqdm import tqdm
from os import path

from src.db_conn.models import GStoreReview


@dataclass
class Review:
    reviewer_id: str = ''
    reviewer_name: str = ''
    reviewer_self_count: str = ''
    reviewer_lang: str = ''
    rating: float = 0
    date_range: str = ''
    review_content: str = ''
    dining_mode: str = ''
    dining_meal_type: str = ''
    pic_url: str = ''
    phone_brand: str = ''
    pic_date: str = ''


class GoogleReviewCrawler:
    def __init__(self, store_id, reviews_url='', reviews_count=0, delay=0, logger=logging.Logger):
        self.store_id = store_id
        self.reviews_url = reviews_url
        self.reviews_api = reviews_url.split('?')[0]
        self.params = [key_idx.split('=') for key_idx in reviews_url.split('?')[-1].split('&')]
        self.params = {key: idx for key, idx in self.params}
        self.headers = {
                    'Referer': 'https://www.google.com.tw/',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; '
                                    'Intel Mac OS X 10_15_7) '
                                    'AppleWebKit/537.36 (KHTML, '
                                    'like Gecko) '
                                    'Chrome/102.0.5005.115 '
                                    'Safari/537.36',
                    'sec-ch-ua': '" Not A;Brand";v="99", '
                                    '"Chromium";v="102", "Google '
                                    'Chrome";v="102"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"macOS"',
                    'x-goog-ext-353267353-bin': 'IM+ACQ=='
                }
        self.r_key = '!1i'
        self.reviews_count=reviews_count
        self.delay=delay
        self.logger=logger

    def run(self) -> list:
        store_reviews = []
        try:
            review_count = 1
            for idx in range(0, self.reviews_count, 10):
                self.params['pb'] = re.sub(r'{}[0-9]+!'.format(self.r_key), '{}{}!'.format(self.r_key, idx), self.params['pb'])
                # print(params)
                response = requests.get(self.reviews_api, params=self.params, headers=self.headers)
                if response.status_code != 200:
                    raise
                    # self.logger.error('response.status_code: {} ...'.format(str(response.status_code)))
                    # self.logger.info('Searching.')
                resp_str = response.content.decode().replace(')]}\'', '')
                reviews = json.loads(resp_str)[2]

                if reviews is None: break
                for review in reviews:
                    review_obj = Review()
                    review_obj.reviewer_id = review[6]
                    review_obj.reviewer_name = review[0][1]
                    review_obj.review_content = review[3]
                    review_obj.rating = float(review[4])
                    review_obj.date_range = review[1]
                    review_obj.reviewer_self_count = review[12][1][1]
                    review_obj.reviewer_lang = review[32]

                    if not (review[49] is None):
                        dining_info = review[49]
                        for di in dining_info:
                            if di[0] == 'GUIDED_DINING_MODE':
                                review_obj.dining_mode = di[2][0][0][1]
                            elif di[0] == 'GUIDED_DINING_MEAL_TYPE':
                                review_obj.dining_meal_type = di[2][0][0][1]
                    
                    if not (review[14] is None):
                        for pics in review[14]:
                            review_obj.pic_url = '{},{}'.format(review_obj.pic_url, pics[6][0])
                            review_obj.phone_brand = pics[21]
                            review_obj.phone_brand = pics[21][6]
                            review_obj.phone_brand = pics[21][6][5]
                            review_obj.phone_brand = pics[21][6][5][2]
                            review_obj.pic_date = ','.join([str(d) for d in pics[21][6][7][0:3]])

                    store_reviews.append(GStoreReview(
                        review_id=review_count,
                        reviewer_id=review_obj.reviewer_id,
                        reviewer_name=review_obj.reviewer_name,
                        reviewer_self_count=review_obj.reviewer_self_count,
                        reviewer_lang=review_obj.reviewer_lang,
                        rating=review_obj.rating,
                        date_range=review_obj.date_range,
                        review_content=review_obj.review_content,
                        dining_mode=review_obj.dining_mode,
                        dining_meal_type=review_obj.dining_meal_type,
                        pic_url=review_obj.pic_url,
                        phone_brand=review_obj.phone_brand,
                        pic_date=review_obj.pic_date,
                        g_store_id=self.store_id
                    ))
                    review_count+=1
                    # print(review_obj)
                time.sleep(self.delay)
        except Exception as exc:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.logger.error('Other Exception: {}, {}, {}'.format(exc_type, fname, exc_tb.tb_lineno))

        return store_reviews
  

if __name__ == '__main__':
    reviews_url = 'https://www.google.com.tw/maps/preview/review/listentitiesreviews?authuser=0&hl=zh-TW&gl=tw&pb=!1m2!1y3776617326788932329!2y17926050799734344169!2m2!1i10!2i10!3e1!4m5!3b1!4b1!5b1!6b1!7b1!5m2!1s7wGwYruYMsSjoAS6wrfoAw!7e81'
    reviews_count = 5008

    logger = logging.getLogger(__name__)
    logger.info('Start job.')
    google_reviews_crawler = GoogleReviewCrawler(reviews_url=reviews_url, reviews_count=reviews_count, delay=0, logger=logger)
    google_reviews_crawler.run()
    logger.info('End job.')

