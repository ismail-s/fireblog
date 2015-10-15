import datetime
import random
from shortuuid import uuid

from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    desc
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Table, ForeignKey
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref,
)

from zope.sqlalchemy import ZopeTransactionExtension


def create_username(context):
    userid = context.current_parameters['userid']
    if not userid:
        userid = uuid()  # Set it to some random thing...
    username = userid[:userid.find('@')]
    while DBSession.query(Users.username).filter_by(username=username).first():
        username += str(random.randrange(0, 9))
    return username


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

post_tags = Table('post_tags', Base.metadata,
                  Column('post_id', Integer, ForeignKey('posts.id')),
                  Column('keyword_id', Integer, ForeignKey('tags.id')))


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(Text, unique=True, default=uuid)
    name = Column(Text, unique=True, index=True, nullable=False)
    created = Column(DateTime, default=datetime.datetime.utcnow,
                     index=True, nullable=False)
    markdown = Column(Text)
    html = Column(Text)
    tags = relationship('Tags', secondary=post_tags, backref='posts')


class Users(Base):
    __tablename__ = 'users'
    # Note userid will be an email address from mozilla persona
    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(Text, unique=True, default=uuid)
    userid = Column(Text, unique=True, index=True, nullable=False)
    username = Column(Text, unique=True, default=create_username)
    group = Column(Text)


class Tags(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(Text, unique=True, default=uuid, nullable=False)
    tag = Column(Text, unique=True, index=True, nullable=False)


class Comments(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(Text, unique=True, default=uuid, nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'))
    author_id = Column(Integer, ForeignKey('users.id'))
    created = Column(
        DateTime, default=datetime.datetime.utcnow, nullable=False)
    comment = Column(Text)

    post = relationship("Post", backref=backref(
        'comments', order_by=desc(created)))
    author = relationship("Users", backref=backref(
        'comments', order_by=desc(created)))
