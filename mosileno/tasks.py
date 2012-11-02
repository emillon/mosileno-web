import feedparser
import transaction

from .models import (
        DBSession,
        Feed,
        User,
        Subscription,
        Item,
        )

from celery.task import task
from pyramid.security import authenticated_userid
from datetime import datetime
from time import mktime

def import_feed(request, url):
    feed = Feed(url)
    DBSession.add(feed)
    me = authenticated_userid(request)
    user = DBSession.query(User).filter(User.name==me).one()
    sub = Subscription(user, feed)
    DBSession.add(sub)
    handlers = request.registry.settings.get('urllib2_handlers', [])
    DBSession.expunge(feed)
    fetch_title.delay(feed.id, handlers=handlers)
    fetch_items.delay(feed.id, handlers=handlers)

@task
def fetch_title(feed_id, handlers=[]):
    feedObj = DBSession.query(Feed).get(feed_id)
    if feedObj is None:
        raise fetch_title.retry(countdown=3)
    feed = feedparser.parse(feedObj.url, handlers=handlers)
    feedObj.title = feed.feed.title
    transaction.commit()

@task
def fetch_items(feed_id, handlers=[]):
    feedObj = DBSession.query(Feed).get(feed_id)
    if feedObj is None:
        raise fetch_items.retry(countdown=3)
    feed = feedparser.parse(feedObj.url, handlers=handlers)
    for item in feed.entries:
        item_date = item.get('updated_parsed',
                item.get('published_parsed', None))
        if item_date is None:
            date = None
        else:
            date = datetime.fromtimestamp(mktime(item_date))
        i = Item(feedObj, title=item.title,
                link=item.link, description=item.description,
                date=date)
        DBSession.add(i)
