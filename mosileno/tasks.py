import feedparser
import transaction

from .models import (
    DBSession,
    Feed,
    User,
    Subscription,
    Item,
)

from celery.decorators import periodic_task
from celery.task import task
from pyramid.security import authenticated_userid
from datetime import datetime, timedelta
from time import mktime


def import_feed(request, url):
    feed = Feed(url)
    DBSession.add(feed)
    me = authenticated_userid(request)
    user = DBSession.query(User).filter(User.name == me).one()
    sub = Subscription(user, feed)
    DBSession.add(sub)
    DBSession.expunge(feed)
    fetch_title.delay(feed.id)
    return feed.id


@task
def fetch_title(feed_id):
    feedObj = DBSession.query(Feed).get(feed_id)
    if feedObj is None:
        raise fetch_title.retry(countdown=3)
    feed = feedparser.parse(feedObj.url)
    if hasattr(feed.feed, 'title'):
        feedObj.title = feed.feed.title
        transaction.commit()
        fetch_items.delay(feed_id)
    else:
        # Probably a web page ; find feeds from metadata
        if 'links' in feed.feed:
            feeds = [l['href']
                     for l in feed.feed['links']
                     if l.get('type', None) == 'application/rss+xml'
                     ]
            feedObj.url = feeds[0]
            transaction.commit()
            raise fetch_title.retry(countdown=3)
        else:
            # Maybe signal to the user?
            DBSession.delete(feedObj)
            transaction.commit()


@task
def fetch_items(feed_id):
    with transaction.manager:
        feedObj = DBSession.query(Feed).get(feed_id)
        if feedObj is None:
            raise fetch_items.retry(countdown=3)
        feed = feedparser.parse(feedObj.url)
        for item in feed.entries:
            guid = item.get('id', None)
            already_in = DBSession.query(Item).filter_by(guid=guid).first()
            if already_in:
                continue
            item_date = item.get('updated_parsed',
                                 item.get('published_parsed', None))
            if item_date is None:
                date = None
            else:
                date = datetime.fromtimestamp(mktime(item_date))
            i = Item(feedObj,
                     title=item.title,
                     link=item.link,
                     description=item.description,
                     date=date,
                     guid=guid,
                     )
            DBSession.add(i)


@periodic_task(run_every=timedelta(minutes=15))
def fetch_all_items():
    with transaction.manager:
        feeds = DBSession.query(Feed.id).all()
        for feed in feeds:
            fetch_items.delay(feed)
