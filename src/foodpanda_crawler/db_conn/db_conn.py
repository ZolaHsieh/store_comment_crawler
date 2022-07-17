from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import NullPool
import logging


class DBObj(object):
    def __init__(self, base, info):
        self.engine = create_engine(info, echo=False)
        base.metadata.create_all(self.engine)

    def _get_db_session(self):
        Session = sessionmaker(bind=self.engine)
        return Session()
    
    def select_all(self, obj_model):
        session = self._get_db_session()
        results = []
        try:
            results = session.query(obj_model).all()
        except Exception as exc:
            pass
        finally:
            session.close()
        return results
        
    def insert(self, obj_):
        session = self._get_db_session()
        try:
            session.add_all(obj_)
            session.commit()
        except Exception as exc:
            session.rollback()
        finally:
            session.close()

    def engine_dispose(self):
        self.engine.dispose()


class StoreReviewsDB(DBObj):
    def __init__(self, base, info):
        super().__init__(base, info)

    def select_store(self, obj_model, name):
        session = self._get_db_session()
        results = []
        try:
            results = session.query(obj_model).filter(obj_model.store.like('%{}%'.format(name))).all()
        except Exception as exc:
            pass
        finally:
            session.close()
        return results

    def select_store_of_city(self, obj_model, store_list, city_name):
        session = self._get_db_session()
        results = []
        try:
            results = session.query(obj_model).filter(obj_model.store.in_(store_list)&(obj_model.city_name==city_name)).all()
        except Exception as exc:
            pass
        finally:
            session.close()
        return results

    def insert_store_df(self, obj_model, store_data):
        session = self._get_db_session()
        try:
            data = store_data.to_dict(orient='records')
            session.bulk_insert_mappings(obj_model, data)
            session.commit()
            
        except Exception as e:
            print(e)
            pass
        finally:
            session.close()


if __name__ == '__main__':
    db_conn_info = 'sqlite:///db/foodpanda_store_info1.db'
    store_reviews_db = StoreReviewsDB(base=Base, info=db_conn_info)

    results = store_reviews_db.select_store(fStore, '肉')
    print(results)

    store_reviews_db.engine_dispose()

    