from sqlalchemy import ForeignKey, Column, String, DateTime, DECIMAL, Integer, Float, Boolean, TEXT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime as dt
from sqlalchemy.sql import func

Base = declarative_base()

class FStore(Base):
    __tablename__ = 'foodpanda_store'
    city_name = Column('city_name', String(16), primary_key=True)
    city_url = Column('city_url', String(256))

    store_id = Column('store_id', String(16), primary_key=True)
    chain_id = Column('chain_id', String(16), primary_key=True)

    store_name = Column('store_name', String(256), primary_key=True)
    rating = Column('rating', String(8))
    store_url = Column('store_url', String(256))

    address = Column('address', String(1024))
    longitude = Column('longitude', String(16))
    latitude = Column('latitude', String(16))
    chk = Column('chk', Boolean)
    record_time = Column(DateTime(timezone=True), default=dt.now)

    # google_store = relationship("GStore", uselist=False, back_populates="foodpanda_store") 
    # fmenu = relationship("foodpanda_store_menu")
    # fschedule = relationship("foodpanda_store_schedule")

    def __repr__(self):
        return "Foodpanda Store: {}, Rating: {}, City: {}, Getting suc: {}"\
        .format(self.store_name, self.rating, self.city_name, self.chk)

    @classmethod
    def find_by_name(cls, session, store):
        return session.query(cls).filter_by(store=store).all()


class FStoreProcessed(Base):
    __tablename__ = 'foodpanda_store_processed'
    city_name = Column('city_name', String(16), primary_key=True)
    new_city_name = Column('new_city_name', String(16))
    store_id = Column('store_id', String(16), primary_key=True)
    chain_id = Column('chain_id', String(16), primary_key=True)
    store_name = Column('store_name', String(256), primary_key=True)
    rating = Column('rating', String(8))
    address = Column('address', String(1024))
    record_time = Column(DateTime(timezone=True), default=dt.now)


class FStoreMenu(Base):
    __tablename__ = 'foodpanda_store_menu'

    dishes_id = Column('dishes_id', String(16), primary_key=True)
    dishes_code = Column('dishes_code', String(64))
    menu_url = Column('menu_url', String(256))
    dishes_name = Column('dishes_name', String(256))
    description = Column('description', String(1024))
    display_price = Column('display_price', String(16))
    master_category_id = Column('master_category_id', String(8))
    category = Column('category', String(128))
    tags = Column('tags', String(128))

    city_name = Column('city_name', String(16), ForeignKey('foodpanda_store.city_name', ondelete="CASCADE"))
    store_id = Column('store_id', String(16), ForeignKey('foodpanda_store.store_id', ondelete="CASCADE"))
    chain_id = Column('chain_id', String(16), ForeignKey('foodpanda_store.chain_id', ondelete="CASCADE"))
    store_name = Column('store_name', String(256), ForeignKey('foodpanda_store.store_name', ondelete="CASCADE"))
    # store_url = Column('store_url', String(256), ForeignKey('foodpanda_store.store_url', ondelete="CASCADE"))
    
    record_time = Column(DateTime(timezone=True), default=dt.now)

    def __repr__(self):
        pass


class FStoreSchedule(Base):
    __tablename__ = 'foodpanda_store_schedule'

    id_ = Column('id', Integer, primary_key=True, autoincrement=True)
    weekday = Column('weekday', String(8))
    opening_type = Column('opening_type', String(16))
    opening_time = Column('opening_time', String(16))
    closing_time = Column('closing_time', String(16))
    record_time = Column(DateTime(timezone=True), default=dt.now)

    city_name = Column('city_name', String(16), ForeignKey('foodpanda_store.city_name', ondelete="CASCADE"))
    store_id = Column('store_id', String(16), ForeignKey('foodpanda_store.store_id', ondelete="CASCADE"))
    chain_id = Column('chain_id', String(16), ForeignKey('foodpanda_store.chain_id', ondelete="CASCADE"))
    store_name = Column('store_name', String(256), ForeignKey('foodpanda_store.store_name', ondelete="CASCADE"))
    # store_url = Column('store_url', String(256), ForeignKey('foodpanda_store.store_url', ondelete="CASCADE"))

    def __repr__(self):
        pass


class GStore(Base):
    __tablename__ = 'google_store'

    name = Column('name', String(256), primary_key=True, nullable=True)
    services = Column('services', String(16), nullable=True)
    # 可能會沒有評論
    avg_rating = Column('avg_rating', Float(precision=1), nullable=True)
    reviews_count = Column('reviews_count', Integer, nullable=True)
    reviews_url = Column('reviews_url', String(256), nullable=True)
    tags = Column('tags', String(128), nullable=True)
    chk = Column('chk', Boolean, nullable=False)
    address = Column('address', String(1024))
    record_time = Column(DateTime(timezone=True), server_default=func.now())

    city_name = Column('city_name', String(16), ForeignKey('foodpanda_store.city_name', ondelete="CASCADE"), primary_key=True,)
    store_id = Column('store_id', String(16), ForeignKey('foodpanda_store.store_id', ondelete="CASCADE"), primary_key=True)
    chain_id = Column('chain_id', String(16), ForeignKey('foodpanda_store.chain_id', ondelete="CASCADE"), primary_key=True)
    store_name = Column('store_name', String(256), ForeignKey('foodpanda_store.store_name', ondelete="CASCADE"))
    # store_url = Column('store_url', String(256), ForeignKey('foodpanda_store.store_url', ondelete="CASCADE"))

    # city = relationship('FStore', uselist=False, foreign_keys=[city_name])
    # store_i = relationship('FStore', uselist=False, foreign_keys=[store_id])
    # chain = relationship('FStore', uselist=False, foreign_keys=[chain_id])
    # store_n = relationship('FStore', uselist=False, foreign_keys=[store_name])
    # store_u = relationship('FStore', uselist=False, foreign_keys=[store_url])
    # foodpanda_store = relationship("FStore", back_populates="google_store") 
    # google_store_review = relationship('GStoreReview', backref="google_store")

    def __repr__(self):
        return "Store: {}, Rating: {}, Reviews Count: {}, Getting suc: {}"\
        .format(self.name, self.avg_rating, self.reviews_count, self.chk)

    @classmethod
    def find_by_name(cls, session, name):
        return session.query(cls).filter_by(name=name).all()


class GStoreReview(Base):
    __tablename__ = 'google_store_review'

    review_id = Column('review_id', String(96), primary_key=True)
    reviewer_id = Column('reviewer_id', String(32), nullable=True)
    reviewer_name = Column('reviewer_name', String(128), nullable=True)
    reviewer_self_count = Column('reviewer_self_count', String(16), nullable=True)
    reviewer_lang = Column('reviewer_lang', String(16), nullable=True)
    rating = Column('rating', Float, nullable=True)
    date_range = Column('date_range', String(16), nullable=True)
    review_content = Column('review_content', TEXT(20000), nullable=True)
    dining_mode = Column('dining_mode', String(16), nullable=True)
    dining_meal_type = Column('dining_meal_type', String(16), nullable=True)
    pic_url = Column('pic_url', TEXT(20000), nullable=True)
    phone_brand = Column('phone_brand', String(64), nullable=True)
    pic_date = Column('pic_date', String(16), nullable=True)
    record_time = Column(DateTime(timezone=True), server_default=func.now())

    city_name = Column('city_name', String(16), ForeignKey('google_store.city_name', ondelete="CASCADE"))
    store_id = Column('store_id', String(16), ForeignKey('google_store.store_id', ondelete="CASCADE"))
    chain_id = Column('chain_id', String(16), ForeignKey('google_store.chain_id', ondelete="CASCADE"))
    store_name = Column('store_name', String(256), ForeignKey('google_store.store_name', ondelete="CASCADE"))
    # store_url = Column('store_url', String(256), ForeignKey('google_store.store_url', ondelete="CASCADE"))
    
    # google_store_city_name = relationship('GStore', back_populates="google_store_review", foreign_keys=city_name)
    # google_store_store_id = relationship('GStore', back_populates="google_store_review", foreign_keys=store_id)
    # google_store_chain_id = relationship('GStore', back_populates="google_store_review", foreign_keys=chain_id)
    # google_store_store_name = relationship('GStore', back_populates="google_store_review", foreign_keys=store_name)
    # google_store_store_url = relationship('GStore', back_populates="google_store_review", foreign_keys=store_url)

    def __repr__(self):
        return "Reviewer: {}, Comment time: {}, Rating: {}"\
        .format(self.reviewer_name, self.date_range, self.rating)

    @classmethod
    def find_by_key_term(cls, session, review_content):
        return session.query(cls).filter_by(review_content=review_content).all()