import feedparser
import transaction
import unidecode
import re

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
import topics_tools


def import_feed(request, url):
    feed = DBSession.query(Feed).filter_by(url=url).first()
    if not feed:
        feed = Feed(url)
        DBSession.add(feed)
    me = authenticated_userid(request)
    user = DBSession.query(User).filter(User.name == me).one()
    sub = Subscription(user, feed)
    DBSession.add(sub)
    DBSession.expunge(feed)
    fetch_title.delay(feed.id)
    return feed.id


def slugify(s):
    s = unidecode.unidecode(s).lower()
    return re.sub(r'\W+', '-', s)


@task
def fetch_title(feed_id):
    feedObj = DBSession.query(Feed).get(feed_id)
    if feedObj is None:
        raise fetch_title.retry(countdown=3)
    feed = feedparser.parse(feedObj.url)
    if hasattr(feed.feed, 'title'):
        title = feed.feed.title
        feedObj.title = title
        slug = slugify(title)
        already_in = DBSession.query(Feed).filter_by(slug=slug).first()
        if already_in:
            slug = "%s%d" % (slug, feedObj.id)
        feedObj.slug = slug
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


def make_guid(feedObj, item):
    """
    Generate a GUID for a feed item.
    """
    if hasattr(item, 'id'):
        return item.id
    # TODO feedid+published date
    if hasattr(item, 'title'):
        # Not really compliant but we have nothing better
        return "link:%d:%s" % (feedObj.id, item.title)


def get_description(item):
    """
    Return the content from a feed item
    """
    if 'content' in item and item.content:
        return item.content[0].value
    return item.description


@task
def fetch_items(feed_id):
    with transaction.manager:
        feedObj = DBSession.query(Feed).get(feed_id)
        if feedObj is None:
            raise fetch_items.retry(countdown=3)
        feed = feedparser.parse(feedObj.url)
        for item in feed.entries:
            guid = make_guid(feedObj, item)
            already_in = DBSession.query(Item).filter_by(guid=guid).first()
            if already_in:
                continue
            item_date = item.get('updated_parsed',
                                 item.get('published_parsed', None))
            if item_date is None:
                date = None
            else:
                date = datetime.fromtimestamp(mktime(item_date))
            description = get_description(item)
            i = Item(feedObj,
                     title=item.title,
                     link=item.get('link', None),
                     description=description,
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


@task
def get_topic_distrib(text):
    """ 
    gets the topics distribution and the extracted text (from Tika) 
    on the form [(topicid, probability)] for P(topic) > epsilon 
    """
    #return lda_model[lda_model.id2word.doc2bow(utils.lemmatize(text))] TODO
    lda = topics_tools.lda_model
    return lda[lda.id2word.doc2bow(topics_tools.tokenize(text))]

