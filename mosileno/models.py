import bcrypt

from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    DateTime,
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
    url = Column(Text, nullable=False)
    title = Column(Text, nullable=True)
    slug = Column(Text, nullable=True, unique=True)
    etag = Column(Text)

    def __init__(self, url):
        self.url = url


class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    feed = Column(Integer, ForeignKey('feeds.id', ondelete='SET NULL'))

    def __init__(self, user, feed):
        self.user = user.id
        self.feed = feed.id


class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    feed = Column(Integer, ForeignKey('feeds.id', ondelete='SET NULL'))
    title = Column(Text)
    link = Column(Text)
    description = Column(Text)
    date = Column(DateTime)
    guid = Column(Text, nullable=False, unique=True)

    def __init__(self,
                 feed,
                 title=None,
                 link=None,
                 description=None,
                 date=None,
                 guid=None,
                 ):
        self.feed = feed.id
        self.title = title
        self.link = link
        self.description = description
        self.date = date
        self.guid = guid


class Invitation(Base):
    __tablename__ = 'invitations'
    id = Column(Integer, primary_key=True)
    code = Column(Text)


class Vote(Base):
    __tablename__ = 'votes'
    id = Column(Integer, primary_key=True)
    value = Column(Integer)  # +1 / -1
    item = Column(Integer, ForeignKey('items.id', ondelete='SET NULL'))
    user = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))

    def __init__(self, value, itemid, userid):
        assert(value == 1 or value == -1)
        self.value = value
        self.item = itemid
        self.user = userid


class Signal(Base):
    __tablename__ = 'signals'
    id = Column(Integer, primary_key=True)
    source_page = Column(Integer)  # 1: home or 2: expandview

    # Codes for action
    # 1: linkup
    # 2: linkdown
    # 3: linkclick
    # 4: linkupcancel
    # 5: linkdowncancel
    action = Column(Integer)
    item = Column(Integer, ForeignKey('items.id', ondelete='SET NULL'))
    user = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))

    sources_ok = ['home', 'expandedview']
    actions_ok = ['linkup',
                  'linkdown',
                  'linkclick',
                  'linkupcancel',
                  'linkdowncancel',
                  ]

    def __init__(self, source, action, itemid, userid):
        assert(source in Signal.sources_ok)
        assert(action in Signal.actions_ok)
        self.source_page = source
        self.action = action
        self.item = itemid
        self.user = userid
