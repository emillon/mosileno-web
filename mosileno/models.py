import bcrypt

from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    DateTime,
    Float,
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
    authenticated_userid,
)

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class RootFactory(object):
    __name__ = ''
    __acl__ = [
        (Allow, Authenticated, 'edit'),
        (Allow, 'admin', 'admin'),
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

    @staticmethod
    def logged_in(request):
        me = authenticated_userid(request)
        return DBSession.query(User).filter_by(name=me).one()


class Feed(Base):
    __tablename__ = 'feeds'
    id = Column(Integer, primary_key=True)
    url = Column(Text, nullable=False)
    title = Column(Text, nullable=True)
    slug = Column(Text, nullable=True, unique=True)
    etag = Column(Text)

    def __init__(self, url):
        self.url = url

    @staticmethod
    def by_slug(slug, fail=True):
        """
        Attempt to find a Feed with given slug.
        exists -> return it
        else   -> fail=True  -> raise an exception
                  fail=False -> return None
        """
        q = DBSession.query(Feed).filter_by(slug=slug)
        if fail:
            return q.one()
        else:
            return q.first()


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


class ItemTopic(Base):
    __tablename__ = 'itemtopics'
    id = Column(Integer, primary_key=True)
    item = Column(Integer, ForeignKey('items.id', ondelete='SET NULL'))
    topic = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)

    def __init__(self, item, topic, weight):
        self.item = item
        self.topic = topic
        self.weight = weight


class ItemTopicName(Base):
    __tablename__ = 'itemtopicnames'
    id = Column(Integer, primary_key=True)
    item = Column(Integer, ForeignKey('items.id', ondelete='SET NULL'))
    topicname = Column(Text, nullable=False)

    def __init__(self, item, topicname):
        self.item = item
        self.topicname = topicname


class ItemScore(Base):
    __tablename__ = 'itemscores'
    id = Column(Integer, primary_key=True)
    item = Column(Integer, ForeignKey('items.id', ondelete='SET NULL'))
    user = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    score = Column(Float, nullable=False)

    def __init__(self, item, user, score):
        self.item = item
        self.user = user
        self.score = score


class UserTopicName(Base):
    __tablename__ = 'usertopicnames'
    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    topicname = Column(Text, nullable=False)

    def __init__(self, user, topicname):
        self.user = user
        self.topicname = topicname
