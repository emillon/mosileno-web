"""
Run inference on all items

(Populate itemtopics table)
"""

from mosileno.models import (
    DBSession,
    Item,
    ItemTopic,
)
from sqlalchemy import create_engine
import transaction
import requests
from mosileno import topics_tools

def get_topic_distrib(text):
    """ 
    gets the topics distribution and the extracted text (from Tika) 
    on the form [(topicid, probability)] for P(topic) > epsilon 
    """
    lda = topics_tools.lda_model
    return lda[lda.id2word.doc2bow(topics_tools.parse(text))]

engine = create_engine('sqlite:///mosileno.sqlite')
DBSession.configure(bind=engine)

items = DBSession.query(Item).all()

for item in items:
    print item.id
    with transaction.manager:
        item = DBSession.query(Item).get(item.id)
        rsp = requests.get('http://localhost:9998/', params={'doc': item.link})
        if 'retval' not in rsp.json:
            continue
        data = rsp.json['retval']
        tops = get_topic_distrib(data)
        for (topic, score) in tops:
            d = ItemTopic(item.id, topic, score)
            DBSession.add(d)
