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

def get_most_relevant_topics(topics_list):
    """
    from a [(topicid, probability)] list (for P(topic) > epsilon),
    it gets the "names" of the most probable topics
    """
    topics_list.sort(cmp=lambda x, y: 1 if x[1] < y[1] else -1)
    topics_list = topics_list[:3] # ARBITRARY (at most 3 topic names)
    topics_id, _ = zip(*topics_list)
    topic_names = topics_tools.lda_topic_names()
    return [topic_names[tid] for tid in topics_id]

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
