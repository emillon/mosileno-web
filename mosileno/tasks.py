import feedparser
import transaction

from .models import (
        DBSession,
        Feed,
        )

from celery.task import task

@task
def fetch_title(feed_id):
    feedObj = DBSession.query(Feed).get(feed_id)
    if feedObj is None:
        raise fetch_title.retry(countdown=3)
    feed = feedparser.parse(feedObj.url)
    feedObj.title = feed.feed.title
    transaction.commit()
