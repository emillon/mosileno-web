import bcrypt

from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.security import (
        Allow,
        Authenticated,
        Deny,
        Everyone,
        )

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class RootFactory(object):
    __name__ = ''
    __acl__ = [
            (Allow, Authenticated, 'edit'),
            ]
    def __init__(self, request):
        pass

class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    value = Column(Integer)

    def __init__(self, name, value):
        self.name = name
        self.value = value

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)

    def __init__(self, login, password, workfactor=12):
        self.name = login
        salt = bcrypt.gensalt(workfactor)
        self.password = bcrypt.hashpw(password, salt)

class Feed(Base):
    __tablename__ = 'feeds'
    id = Column(Integer, primary_key=True)
    url = Column(Text, unique=True, nullable=False)
    title = Column(Text, unique=True, nullable=True)

    def __init__(self, url):
        self.url = url

class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey('users.id'))
    feed = Column(Integer, ForeignKey('feeds.id'))

    def __init__(self, user, feed):
        self.user = user.id
        self.feed = feed.id
