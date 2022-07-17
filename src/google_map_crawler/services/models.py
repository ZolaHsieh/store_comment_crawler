from sqlalchemy import ForeignKey, Column, String, DateTime, DECIMAL, Integer, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class FStore(Base):
    __tablename__ = 'foodpanda_store_list'
    store_id = Column('store_id', String, primary_key=True)
    store = Column('store', String, primary_key=True)
    rating = Column('rating', String)
    store_url = Column('store_url', String, primary_key=True)
    city_name = Column('city_name', String, primary_key=True)
    city_url = Column('city_url', String)
    chk = Column('chk', String)

    # g_store = relationship('GStore' , back_populates='foodpanda_store_list')

    def __repr__(self):
        return "Foodpanda Store: {}, Rating: {}, City: {}, Getting suc: {}"\
        .format(self.store, self.rating, self.city_name, self.chk)

    @classmethod
    def find_by_name(cls, session, store):
        return session.query(cls).filter_by(store=store).all()


class FStoreMenu(Base):
    __tablename__ = 'foodpanda_store_menu'

    id = Column('id', String, primary_key=True)
    
    store_name = Column('store_name', String, primary_key=True)
    address = Column('address', String)
    longitude = Column('longitude', String)
    latitude = Column('latitude', String)
    menu_url = Column('menu_url', String)
    code = Column('code', String)
    name = Column('name', String)
    description = Column('description', String)
    display_price = Column('display_price', String)
    master_category_id = Column('master_category_id', String)
    category = Column('category', String)
    tags = Column('tags', String)

    def __repr__(self):
        pass


class FStoreSchedule(Base):
    __tablename__ = 'foodpanda_store_schedule'
    id = Column('id', String, primary_key=True)
    store_name = Column('store_name', String, primary_key=True)
    weekday = Column('weekday', String)
    opening_type = Column('opening_type', String)
    opening_time = Column('opening_time', String) 
    closing_time = Column('closing_time', String)
    
    def __repr__(self):
        pass
        

class GStore(Base):
    __tablename__ = 'g_store'
    # id = Column('id', Integer, primary_key=True, autoincrement=True)
    # store
    name = Column('name', String, nullable=True, primary_key=True)
    services = Column('services', String, nullable=True)
    # 可能會沒有評論
    avg_rating = Column('avg_rating', Float(precision=1), nullable=True)
    reviews_count = Column('reviews_count', Integer, nullable=True)
    reviews_url = Column('reviews_url', String, nullable=True)
    tags = Column('tags', String, nullable=True)
    chk = Column('chk', String, nullable=False)
    f_store_id = Column('f_store_id', String, ForeignKey('foodpanda_store_list.store_id'), primary_key=True)
    record_time = Column(DateTime(timezone=True), server_default=func.now())

    # f_store = relationship('FStore', back_populates='g_store')
    g_store_review = relationship('GStoreReview')

    def __repr__(self):
        return "Store: {}, Rating: {}, Reviews Count: {}, Getting suc: {}"\
        .format(self.name, self.avg_rating, self.reviews_count, self.chk)

    @classmethod
    def find_by_name(cls, session, name):
        return session.query(cls).filter_by(name=name).all()


class GStoreReview(Base):
    __tablename__ = 'g_store_review'

    # id = Column('id', Integer, primary_key=True, autoincrement=True)
    review_id = Column('review_id', Integer, primary_key=True)
    reviewer_id = Column('reviewer_id', String, nullable=True, primary_key=True)
    reviewer_name = Column('reviewer_name', String, nullable=True)
    reviewer_self_count = Column('reviewer_self_count', String, nullable=True)
    reviewer_lang = Column('reviewer_lang', String, nullable=True)
    rating = Column('rating', Float, nullable=True)
    date_range = Column('date_range', String, nullable=True)
    review_content = Column('review_content', String, nullable=True)
    dining_mode = Column('dining_mode', String, nullable=True)
    dining_meal_type = Column('dining_meal_type', String, nullable=True)
    pic_url = Column('pic_url', String, nullable=True)
    phone_brand = Column('phone_brand', String, nullable=True)
    pic_date = Column('pic_date', String, nullable=True)
    g_store_id = Column(Integer, ForeignKey('g_store.f_store_id'), primary_key=True)
    record_time = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return "Reviewer: {}, Comment time: {}, Rating: {}, Content: {}"\
        .format(self.reviewer_name, self.date_range, self.rating, self.review_content)

    @classmethod
    def find_by_key_term(cls, session, review_content):
        return session.query(cls).filter_by(review_content=review_content).all()

