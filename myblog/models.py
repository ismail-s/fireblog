import datetime
from shortuuid import uuid

from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    DateTime
    )

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Table, ForeignKey
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

post_tags = Table('post_tags', Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id')),
    Column('keyword_id', Integer, ForeignKey('tags.id')))

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, nullable = False)
    uuid = Column(Text, unique = True, default = uuid)
    name = Column(Text, unique = True, index = True, nullable = False)
    created = Column(DateTime, default=datetime.datetime.utcnow, index = True, nullable = False)
    markdown = Column(Text)
    html = Column(Integer)
    tags = relationship('Tags', secondary=post_tags, backref='posts')

class Users(Base):
    __tablename__ = 'users'
    # Note userid will be an email address from mozilla persona
    id = Column(Integer, primary_key = True, nullable = False)
    uuid = Column(Text, unique = True, default = uuid)
    userid = Column(Text, unique = True, index = True, nullable = False)
    group = Column(Text)

class Tags(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key = True, nullable = False)
    uuid = Column(Text, unique = True, default = uuid, nullable = False)
    tag = Column(Text, unique = True, index = True, nullable = False)
