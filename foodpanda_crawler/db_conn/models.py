from sqlalchemy import ForeignKey, Column, String, DateTime, DECIMAL, Integer, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class FStore(Base):
    __tablename__ = 'foodpanda_store'
    city_name = Column('city_name', String, primary_key=True)
    city_url = Column('city_url', String)

    store_id = Column('store_id', String, primary_key=True)
    chain_id = Column('chain_id', String, primary_key=True)

    store_name = Column('store_name', String, primary_key=True)
    rating = Column('rating', String)
    store_url = Column('store_url', String, primary_key=True)
    
    address = Column('address', String)
    longitude = Column('longitude', String)
    latitude = Column('latitude', String)
    chk = Column('chk', Boolean)
    record_time = Column(DateTime(timezone=True), server_default=func.now())
    
    # fmenu = relationship("foodpanda_store_menu")
    # fschedule = relationship("foodpanda_store_schedule")

    def __repr__(self):
        return "Foodpanda Store: {}, Rating: {}, City: {}, Getting suc: {}"\
        .format(self.store_name, self.rating, self.city_name, self.chk)

    @classmethod
    def find_by_name(cls, session, store):
        return session.query(cls).filter_by(store=store).all()


class FStoreMenu(Base):
    __tablename__ = 'foodpanda_store_menu'

    dishes_id = Column('dishes_id', String, primary_key=True)
    dishes_code = Column('dishes_code', String)
    menu_url = Column('menu_url', String)
    dishes_name = Column('dishes_name', String)
    description = Column('description', String)
    display_price = Column('display_price', String)
    master_category_id = Column('master_category_id', String)
    category = Column('category', String)
    tags = Column('tags', String)
    
    store_id = Column('store_id', String, ForeignKey('foodpanda_store.store_id'))
    record_time = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        pass


class FStoreSchedule(Base):
    __tablename__ = 'foodpanda_store_schedule'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    store_id = Column('store_id', String, ForeignKey('foodpanda_store.store_id'))
    store_name = Column('store_name', String)
    weekday = Column('weekday', String)
    opening_type = Column('opening_type', String)
    opening_time = Column('opening_time', String) 
    closing_time = Column('closing_time', String)
    record_time = Column(DateTime(timezone=True), server_default=func.now())

    
    def __repr__(self):
        pass
        