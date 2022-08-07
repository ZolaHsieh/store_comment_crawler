from sqlalchemy import create_engine, literal
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists
from src.db_conn.models import Base, FStore, FStoreMenu, FStoreSchedule
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
            results = session.query(obj_model).filter(obj_model.store_name.like('%{}%'.format(name))).all()
        except Exception as exc:
            pass
        finally:
            session.close()
        return results

    def select_store_of_city(self, obj_model, store_list, city_name):
        session = self._get_db_session()
        results = []
        try:
            results = session.query(obj_model).filter(obj_model.store_name.in_(store_list), obj_model.city_name==city_name).all()
        except Exception as e:
            print(e)
            pass
        finally:
            session.close()
        return results

    def select_uncheck_store(self, obj_model):
        session = self._get_db_session()
        results = []
        try:
            results = session.query(obj_model).filter(obj_model.chk==False, obj_model.store_id!='').all()
            
        except Exception as exc:
            pass
        finally:
            session.close()
        return results

    def select_chain_store(self, obj_model):
        session = self._get_db_session()
        results = []
        try:
            results = session.query(obj_model).filter(obj_model.chain_id!='', obj_model.store_id=='').all()
        except Exception as exc:
            pass
        finally:
            session.close()
        return results

    def insert_store_df(self, obj_model, store_data):
        session = self._get_db_session()
        try:
            # data = store_data.to_dict(orient='records')
            # session.bulk_insert_mappings(obj_model, data)
            for data in store_data.to_dict(orient='records'):
                q = session.query(obj_model).filter(obj_model.city_name==data['city_name'], 
                                                                        obj_model.store_id==data['store_id'],
                                                                        obj_model.chain_id==data['chain_id'],
                                                                        obj_model.store_name==data['store_name'],
                                                                        obj_model.store_url==data['store_url'])
                if not session.query(literal(True)).filter(q.exists()).scalar():
                    print('not exist', data['store_name'])
                    data = obj_model(**data)
                    session.add(data)
                    session.commit()

        except Exception as e:
            print(e)
            pass
        finally:
            session.close()

    def insert_menu_df(self, obj_model, menu_data):
        session = self._get_db_session()
        try:
            for data in menu_data.to_dict(orient='records'):
                q = session.query(obj_model).filter(obj_model.dishes_id==data['dishes_id'])
                if not session.query(literal(True)).filter(q.exists()).scalar():
                    data = obj_model(**data)
                    session.add(data)
                session.commit()

        except Exception as e:
            print(e)
            pass
        finally:
            session.close()

    def insert_schedule_df(self, obj_model, s_data):
        session = self._get_db_session()
        # conn = self.engine.connect()
        try:
            data = [obj_model(**s) for s in s_data.to_dict(orient='records')]
            session.add_all(data)
            session.commit()

        except Exception as e:
            print(e)
            pass
        finally:
            session.close()

    def update_store_info(self, obj_model, update_dict):
        session = self._get_db_session()
        try:
            session.query(obj_model).\
                    filter((obj_model.city_name==update_dict['city_name']),
                            (obj_model.store_name==update_dict['store_name']),
                            (obj_model.chain_id==update_dict['chain_id'])).\
                    update({'store_id':update_dict['store_id'],
                            'store_url':update_dict['web_url']})
            session.commit()
        except Exception as exc:
            pass
        finally:
            session.close()

    def update_store_id(self, obj_model, update_dict):
        session = self._get_db_session()
        try:
            session.query(obj_model).\
                    filter((obj_model.chain_id==update_dict['chain_id']),
                            (obj_model.store_name==update_dict['store_name']),
                            (obj_model.city_name==update_dict['city_name'])).\
                    update({'store_id':update_dict['store_id'],
                            'store_url':update_dict['store_url']})
            session.commit()
        except Exception as exc:
            pass
        finally:
            session.close()

if __name__ == '__main__':
    db_conn_info = 'sqlite:///db/foodpanda_store_info1.db'
    store_reviews_db = StoreReviewsDB(base=Base, info=db_conn_info)

    results = store_reviews_db.select_store(ＦStore, '肉')
    print(results)

    store_reviews_db.engine_dispose()

    