from sqlalchemy import create_engine
from mosileno.models import (
    DBSession,
    Item,
    ItemTopic,
    ItemTopicName,
)
import topics_tools
import transaction

def get_most_relevant_topics(topics_list):
    """
    from a [(topicid, probability)] list (for P(topic) > epsilon),
    it gets the "names" of the most probable topics
    """
    topics_list.sort(cmp=lambda x, y: 1 if x[1] < y[1] else -1)
    topics_list = topics_list[:3] # ARBITRARY (at most 3 topic names)
    topics_id, _ = zip(*topics_list)
    return [topics_tools.lda_topic_names[tid] for tid in topics_id]

engine = create_engine('sqlite:///mosileno.sqlite')
DBSession.configure(bind=engine)

items = DBSession.query(Item).all()

for item in items:
    with transaction.manager:
        print item.id
        res = DBSession.query(ItemTopic).filter_by(item=item.id).all()
        if res:
            topics = get_most_relevant_topics([(r.topic, r.weight) for r in res])
        else:
            topics = []
        for t in topics:
            tn = ItemTopicName(item.id, t)
            DBSession.add(tn)
