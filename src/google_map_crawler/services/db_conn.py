from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import NullPool
from .models import Base, GStore, FStore
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
            print(str(exc))
        finally:
            session.close()
        return results
        
    def insert_all(self, objs):
        session = self._get_db_session()
        try:
            session.add_all(objs)
            session.commit()
        except Exception as exc:
            print(str(exc))
            session.rollback()
        finally:
            session.close()

    def engine_dispose(self):
        self.engine.dispose()


class StoreReviewsDB(DBObj):
    def __init__(self, base, info):
        super().__init__(base, info)

    def select_store_name(self, obj_model, name):
        session = self._get_db_session()
        results = []
        try:
            results = session.query(obj_model).filter(obj_model.store.like('%{}%'.format(name))).all()
        except Exception as exc:
            pass
        finally:
            session.close()
        return results

    def get_checked_store(self, obj_model):
        session = self._get_db_session()
        results = []
        try:
            results = session.query(obj_model).filter(obj_model.chk.like('Y')).all()
        except Exception as exc:
            pass
        finally:
            session.close()
        return results


if __name__ == '__main__':
    db_conn_info = 'sqlite:///db/foodpanda_store_info.db'
    store_reviews_db = StoreReviewsDB(base=Base, info=db_conn_info)

    results = store_reviews_db.select_store(FStore, '肉')
    print(results)

    store_reviews_db.engine_dispose()

    