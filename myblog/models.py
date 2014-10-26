import datetime

from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    DateTime
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, nullable = False)
    name = Column(Text, unique = True, index = True, nullable = False)
    created = Column(DateTime, default=datetime.datetime.utcnow, index = True, nullable = False)
    markdown = Column(Text)
    html = Column(Integer)

class Users(Base):
    __tablename__ = 'users'
    # Note userid will be an email address from mozilla persona
    id = Column(Integer, primary_key = True, nullable = False)
    userid = Column(Text, unique = True, index = True, nullable = False)
    group = Column(Text)
