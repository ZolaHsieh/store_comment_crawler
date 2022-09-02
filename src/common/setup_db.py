import os
from src.db_conn.db_conn import StoreReviewsDB
from src.db_conn.models import Base


def setup(db_type):
    '''
    all db_type: mariadb/sqlite
    '''
    db_conn_info = ''

    if db_type == 'mariadb':
        _user = os.getenv('MYSQL_USER')
        _password = os.getenv('MYSQL_PASSWORD')
        _host = 'db'
        _port = 3306
        _database=os.getenv('MYSQL_DATABASE')
        
        db_conn_info = f'mysql+pymysql://{_user}:{_password}@{_host}:{_port}/{_database}?charset=utf8mb4'
    else:
        db_conn_info = 'sqlite:///./db/foodpanda_store_info.db?charset=utf8'

    store_reviews_db = StoreReviewsDB(base=Base, info=db_conn_info)

    return store_reviews_db