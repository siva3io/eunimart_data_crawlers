import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, create_engine, ForeignKey, BLOB, Date, Boolean, Table, Float, ARRAY, TIMESTAMP, DateTime
from sqlalchemy.types import JSON
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_mixins import SerializeMixin

from .helpers import memoise

Base = declarative_base()

@memoise
def get_session(url):
    engine = create_engine(url, pool_pre_ping=True)
    Session = sessionmaker(bind = engine)
    session = Session()
    return session

def create_tables(url, table_name="products"):
    engine = create_engine(url, pool_pre_ping=True)
    Base.metadata.create_all(engine, [Base.metadata.tables[table_name]],checkfirst=True)
    

class MyBase(Base, SerializeMixin):
    __abstract__ = True
    def __repr__(self):
        name = self.name if hasattr(self, "name") else self.id
        return "{}('{}')".format(self.__class__.__name__, name)


class Products(MyBase):
    __tablename__           = 'products'
    id                      = Column(Integer, primary_key=True)
    marketplace_id          = Column(String)
    pid                     = Column(String)
    marketplace             = Column(String)
    url                     = Column(String)
    is_best_seller          = Column(String)
    position                = Column(String)
    page_no                 = Column(String)
    category                = Column(String)
    sub_category_1          = Column(String)
    sub_category_2          = Column(String)
    description_list        = Column(String)
    from_manufacturer       = Column(String)
    highlights              = Column(String)
    image_1                 = Column(String)
    image_2                 = Column(String)
    image_3                 = Column(String)
    image_4                 = Column(String)
    image_5                 = Column(String)
    image_6                 = Column(String)
    image_7                 = Column(String)
    image_8                 = Column(String)
    image_9                 = Column(String)
    listing_price           = Column(String)
    no_of_answered          = Column(String)
    other_sellers           = Column(JSON) 
    product_title           = Column(String)
    rating                  = Column(String)
    rating_details          = Column(ARRAY(String))
    review_link             = Column(String)
    reviews                 = Column(String)
    saved_price             = Column(String)
    selling_price           = Column(String)
    shipping_price          = Column(String)
    similar_buy             = Column(JSON) 
    similar_views           = Column(JSON) 
    specifications          = Column(JSON) 
    store_address           = Column(String)
    store_description       = Column(String)
    store_help_contact      = Column(String)
    store_link              = Column(String)
    store_name              = Column(String)
    store_overall_rating    = Column(JSON)
    store_rating            = Column(String)
    style_variant           = Column(String)
    tax_info                = Column(String)
    seller_info             = Column(String)
    store_info              = Column(String)
    no_of_ratings           = Column(String)
    created_date            = Column(DateTime, default=datetime.datetime.utcnow)
    updated_date            = Column(DateTime, default=datetime.datetime.utcnow)


class Reviews(MyBase):
    __tablename__ = 'reviews'
    id                          =   Column(Integer, primary_key=True)
    pid                         =   Column(String)
    marketplace                 =   Column(String)
    url                         =   Column(String)
    sub_category_8              =   Column(String)
    file_path                   =   Column(String)
    user_profile_link           =   Column(String)
    user_profile                =   Column(String) 
    review_title                =   Column(String)
    review_date                 =   Column(String)
    rating                      =   Column(String)
    verified_purchase           =   Column(String)
    review_image_1              =   Column(String)
    review_image_2              =   Column(String)
    review_image_3              =   Column(String)
    review_image_4              =   Column(String)
    review_image_5              =   Column(String)
    review_image_6              =   Column(String)
    review_image_7              =   Column(String)
    review_image_8              =   Column(String)
    review_body                 =   Column(String)
    rating_details              =   Column(JSON)
    total_review_count          =   Column(String)
    avg_rating                  =   Column(String)
    created_date                =   Column(DateTime, default=datetime.datetime.utcnow)
    updated_date                =   Column(DateTime, default=datetime.datetime.utcnow)

class BestSellerTable(MyBase):

    __tablename__ = 'best_seller'
    id                          =   Column(Integer, primary_key=True)
    pid                         =   Column(String)
    marketplace                 =   Column(String)
    url                         =   Column(String)
    marketplace_id              =   Column(String)
    category                    =   Column(String)
    sub_category_1              =   Column(String)
    sub_category_2              =   Column(String)
    sub_category_3              =   Column(String)
    sub_category_4              =   Column(String)
    sub_category_5              =   Column(String)
    product_image_6             =   Column(String)
    product_image_7             =   Column(String)
    product_image_8             =   Column(String)
    product_title               =   Column(String)
    product_rating              =   Column(String)
    product_price               =   Column(String)
    store_name                  =   Column(String)
    store_link                  =   Column(String)   
    store_rating                =   Column(String)
    store_description           =   Column(String)
    store_address               =   Column(String)
    store_overall_rating        =   Column(JSON)
    store_help_contact          =   Column(String)
    other_sellers               =   Column(JSON)
    best_selling_rank           =   Column(String)
    top_seller                  =   Column(String)
    position                    =   Column(String)
    created_date                =   Column(DateTime, default=datetime.datetime.utcnow)
    updated_date                =   Column(DateTime, default=datetime.datetime.utcnow)



class BestSellerTask(MyBase):
    __tablename__ = "best_seller_tasks"
    id              =   Column(Integer, primary_key=True)
    hierarchy       =   Column(String)
    marketplace     =   Column(String)
    url             =   Column(String)
    type =   Column(String)
    last_crawled    =   Column(TIMESTAMP)


