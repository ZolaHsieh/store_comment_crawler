from unittest import result
from sqlalchemy import create_engine, literal
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists
from src.db_conn.models import Base, FStore, FStoreMenu, FStoreSchedule
import logging
from sqlalchemy import insert, tuple_


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
            print(exc)
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
            results = session.query(obj_model).filter(obj_model.store_name.like(f'%{name}%')).all()
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
    
    def select_f_store_to_update(self, f_store, g_store, g_exist=False):
        session = self._get_db_session()
        results = []
        try:
            all_g_stores = session.query(g_store).all()
            obj_key = [(obj.city_name, obj.store_id, obj.chain_id, obj.store_name) for obj in all_g_stores]
            
            filter_exp = tuple_(f_store.city_name, f_store.store_id, f_store.chain_id, f_store.store_name).in_(obj_key)
            if g_exist:
                results = session.query(f_store).filter(filter_exp).all()
            else:
                results = session.query(f_store).filter(~filter_exp).all()
        except Exception as e:
            print(e)
            pass
        finally:
            session.close()
        return results

    def select_check_store(self, obj_model):
        session = self._get_db_session()
        results = []
        try:
            results = session.query(obj_model).filter(obj_model.chk==True, obj_model.store_id!='').all()
        except Exception as exc:
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
        
    def delsert_g_reviews(self, obj_model, objs):
        session = self._get_db_session()
        suc_bool = False
        try:
            # obj_ids = {obj.review_id: obj for obj in objs}
            obj_key = [(obj.city_name, obj.store_id, obj.chain_id, obj.store_name) for obj in objs]
            session.query(obj_model).filter(tuple_(obj_model.city_name, obj_model.store_id, obj_model.chain_id, obj_model.store_name).in_(obj_key)).delete()
            session.add_all(objs)
            session.commit()
            suc_bool = True
        except Exception as exc:
            print(exc)
            session.rollback()
        finally:
            session.close()
        return suc_bool

    def upsert_g_reviews(self, obj_model, objs):
        session = self._get_db_session()
        try:
            obj_ids = {obj.review_id: obj for obj in objs}
            for each_ in session.query(obj_model).filter(obj_model.review_id.in_(obj_ids.keys())).all():
                # session.merge(obj_ids.pop(each_.review_id))
                obj_ids.pop(each_.review_id)
            session.add_all(obj_ids.values())
            session.commit()
        except Exception as exc:
            print(exc)
            session.rollback()
        finally:
            session.close()
    
    def upsert_g_store(self, obj_model, obj):
        session = self._get_db_session()
        try:
            obj_key = [(obj.name, obj.city_name, obj.store_id, obj.chain_id)]
            results = session.query(obj_model).filter(tuple_(obj_model.name,
                                                                obj_model.city_name,
                                                                obj_model.store_id, 
                                                                obj_model.chain_id).in_(obj_key)).all()
            if results:
                session.merge(obj)
            else:
                session.add(obj)
            session.commit()

        except Exception as exc:
            print(exc)
            session.rollback()
        finally:
            session.close()

    def insert_store_df(self, obj_model, store_data):
        session = self._get_db_session()
        try:
            # data = store_data.to_dict(orient='records')
            # session.bulk_insert_mappings(obj_model, data)
            for data in store_data.to_dict(orient='records'):
                q = session.query(obj_model).filter(obj_model.city_name==data['city_name'], 
                                                                        obj_model.store_id==data['store_id'],
                                                                        obj_model.chain_id==data['chain_id'],
                                                                        obj_model.store_name==data['store_name'])
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
                            (obj_model.store_id==update_dict['store_id'])).\
                    update({'address':update_dict['address'],
                            'longitude':update_dict['longitude'],
                            'latitude':update_dict['latitude'],
                            'chk':True
                            })
            session.commit()
        except Exception as exc:
            print(str(exc))
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

    