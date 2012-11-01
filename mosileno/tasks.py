import feedparser
import transaction

from .models import (
        DBSession,
        Feed,
        User,
        Subscription,
        )

from celery.task import task
from pyramid.security import authenticated_userid

def import_feed(request, url):
    feed = Feed(url)
    DBSession.add(feed)
    me = authenticated_userid(request)
    user = DBSession.query(User).filter(User.name==me).one()
    sub = Subscription(user, feed)
    DBSession.add(sub)
    fetch_title.delay(feed.id)

@task
def fetch_title(feed_id):
    feedObj = DBSession.query(Feed).get(feed_id)
    if feedObj is None:
        raise fetch_title.retry(countdown=3)
    feed = feedparser.parse(feedObj.url)
    feedObj.title = feed.feed.title
    transaction.commit()
