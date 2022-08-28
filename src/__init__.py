import os
from src.common.setup_logger import setup
from src.db_conn.db_conn import StoreReviewsDB
from src.db_conn.models import Base


_user = os.getenv('MYSQL_USER')
_password = os.getenv('MYSQL_PASSWORD')
_host = 'db'
_port = 3306
_database=os.getenv('MYSQL_DATABASE')

logging_ = setup()
# db_conn_info = 'sqlite:///./db/foodpanda_store_info.db?charset=utf8'
db_conn_info = f'mysql+pymysql://{_user}:{_password}@{_host}:{_port}/{_database}?charset=utf8'
store_reviews_db = StoreReviewsDB(base=Base, info=db_conn_info)
