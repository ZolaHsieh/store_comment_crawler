from ast import Raise
import time
import logging
import re
import json
import sys
# from retry import retry
# from pprint import pprint
from os import path
from dataclasses import dataclass
from selenium import webdriver
# from seleniumwire import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.db_conn.models import GStore

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(name)s][%(levelname)5s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

def process_browser_logs_for_network_request_url(review_api_url, logs):
    for entry in logs:
        log = json.loads(entry['message'])['message']
        if ('Network.request' in log['method'] and 'request' in log['params']):
            if review_api_url in log['params']['request']['url']:
                yield log['params']['request']['url']
                # yield log


@dataclass
class GoogleStoreInfo:
    name: str = ''
    avg_rating: float = 0
    category:str = ''
    services: str = ''
    reviews_count: int = 0
    reviews_url: str = ''
    tags: str = ''
    

class GoogleStoreCrawler:
    def __init__(self, driver_path='./src/driver/chromedriver', delay=5, logger=logging.Logger):
        chrome_options = Options()
        # chrome_options.add_argument("--disable-notifications")
        chrome_service=Service(driver_path)
        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
        self.chrome_driver = webdriver.Chrome(
            service=chrome_service, 
            options=chrome_options,
            desired_capabilities=capabilities
        )
        self.chrome_map_url = 'https://www.google.com.tw/maps'
        self.review_api_url = '/preview/review/listentitiesreviews'
        self.delay=delay
        self.logger=logger
        self.logger.info('Start google driver.')
        
    def _close_session(self):
        self.chrome_driver.close()
        self.chrome_driver.quit()

    def _wait_for_elements_ready_and_find(self, by, text):
        # elements = [webdriver.remote.webelement.WebElement]
        elements = [False]
        try:
            WebDriverWait(self.chrome_driver, self.delay).until(EC.presence_of_all_elements_located((by, text)))
            WebDriverWait(self.chrome_driver, self.delay).until(EC.visibility_of_all_elements_located((by, text)))
            elements = self.chrome_driver.find_elements(by, text)
        except TimeoutException:
            self.logger.error('wait_for_element_ready TimeoutException')
        return elements


    def run(self, search_context, f_store_id) -> GStore:
        store_info  = GoogleStoreInfo()
        suc_bool = 'N'
        try:
            # 開啟chrome with google maps web page
            self.chrome_driver.implicitly_wait(self.delay)
            self.chrome_driver.maximize_window()
            self.chrome_driver.get(self.chrome_map_url)
            self.logger.info('Open google maps web page.')
                # action.ActionChains(chrome)

            # 尋找搜尋框與輸入文字 & 搜尋
            search_input = self._wait_for_elements_ready_and_find(By.XPATH, '//input[@name="q"]')[0]
            search_input.send_keys(search_context)
            self.logger.info('Input context - {}'.format(search_context))
            search_button = self._wait_for_elements_ready_and_find(By.ID, 'searchbox-searchbutton')[0]
            search_button.click()
            self.logger.info('Searching store.')

            check_get_uniq_store = self._wait_for_elements_ready_and_find(By.XPATH, '//h1[@class="DUwDvf fontHeadlineLarge"]/span[1]')[0]
            if not check_get_uniq_store:
                raise NoSuchElementException('Uniq store not found !!')

            # 取得google店家名稱
            g_store_name = self._wait_for_elements_ready_and_find(By.XPATH, '//h1[@class="DUwDvf fontHeadlineLarge"]/span[1]')[0]
            store_info.name = g_store_name.text
            self.logger.info('Getting stroe - {}'.format(store_info.name))

            # avg_rating
            g_avg_rating = self._wait_for_elements_ready_and_find(By.XPATH, '//div[@class="F7nice mmu3tf"]/span/span/span[1]')[0]
            store_info.avg_rating = float(g_avg_rating.text)
            self.logger.info('Getting store average rating - {}'.format(store_info.avg_rating))

            # 類型
            g_category = self._wait_for_elements_ready_and_find(By.XPATH, '//div[@class="F7nice mmu3tf"]/span/span/span[1]')[0]
            store_info.category = g_category.text
            self.logger.info('Getting store category - {}'.format(store_info.category))

            # 內用/外帶/外送
            g_services = self._wait_for_elements_ready_and_find(By.XPATH, '//div[@class="E0DTEd"]/div')
            store_info.services = ','.join([service.get_attribute('aria-label') for service in g_services])
            self.logger.info('Getting store service type - {}'.format(store_info.services))

            # 電話

            # 地址

            # 按下更多評論
            more_reviews_button = self._wait_for_elements_ready_and_find(By.XPATH, '//span[@class="F7nice mmu3tf"]/*/button[@class="DkEaL"]')[0]
            reviews_count_str = re.findall(r'\d+', more_reviews_button.get_attribute('aria-label'), re.I)
            reviews_count = int(''.join(str(str_) for str_ in reviews_count_str))
            more_reviews_button.click()
            store_info.reviews_count = reviews_count
            self.logger.info('Click more reviews. Count: {}'.format(store_info.reviews_count))
            
            # 取得店家tag  
            reviews_tags = self._wait_for_elements_ready_and_find(By.XPATH, 
                                                                '//div[@class="m6QErb tLjsW"]/*//span[@class="uEubGf fontBodyMedium" and not (contains(text(), "+"))]')
            store_info.tags = ','.join([str(r_tag.text) for r_tag in reviews_tags[1:]])
            self.logger.info('Get review tags: {}'.format(store_info.tags))

            # 評論scroll到最下方最後一則評論
            scrollable_pane = self.chrome_driver.find_element(By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf')
            WebDriverWait(self.chrome_driver, self.delay).until(EC.presence_of_element_located((By.XPATH, 
                                                                                                '//div[@class="jftiEf fontBodyMedium"]')))
            self.chrome_driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_pane)

            # 取得評論 requests (1筆)
            logs = self.chrome_driver.get_log('performance')
            urls = process_browser_logs_for_network_request_url('{}{}'.format(self.chrome_map_url, self.review_api_url),logs)
            # with open('logs', 'wt') as out:
            #     for url in urls:
            #         pprint(url, stream=out)
            for url in urls: store_info.reviews_url = url
            self.logger.info('Get review request api: {}'.format(store_info.reviews_url))

            if (not store_info.reviews_url) or (not store_info.tags) or (not store_info.reviews_url): 
                raise Exception('Reviews Url Null !!')
            suc_bool = 'Y'

        except NoSuchElementException as exc:
            self.logger.error('NoSuchElementException: {}'.format(str(exc)))
        except Exception as exc:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.logger.error('Other Exception: {}, {}, {}'.format(exc_type, fname, exc_tb.tb_lineno))
        finally:
            g_store = GStore(name=store_info.name,
                            avg_rating=store_info.avg_rating,
                            services=store_info.services,
                            reviews_count=store_info.reviews_count,
                            reviews_url=store_info.reviews_url,
                            tags=store_info.tags,
                            chk=suc_bool,
                            f_store_id=f_store_id)
            self._close_session()
            self.logger.info('Closing google driver session.')
        
        return g_store
        

if __name__ == '__main__':
    # sample
    country = ''
    administrative_area = '台北市大安區忠孝東路四段205巷7弄9號(斜對面)' #柒息地串燒屋(台北吉延店)
    postal_code = ''
    store_name='一甲子 東區烤肉' # 台北市大安區延吉街99號
    search_context = '{store_name} {administrative_area}'.format(country=country, administrative_area=administrative_area, 
                        postal_code=postal_code, store_name=store_name)


    logger = logging.getLogger(__name__)
    logger.info('Start job.')
    g_review_crawler = GoogleStoreCrawler(delay=10, logger=logger)
    g_store = g_review_crawler.run(search_context=search_context, f_store_id='0000')

    print(g_store)
    logger.info('End job.')