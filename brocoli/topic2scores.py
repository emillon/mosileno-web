import pickle
import sys
import topics_tools
from gensim import utils
from sqlalchemy import create_engine
import transaction
from mosileno.models import *
import operator

if len(sys.argv) <= 1:
    print "Usage: topic2scores.py username user.params"
    sys.exit(1)

username = sys.argv[1]
param_file = sys.argv[2]

with open(param_file) as f:
    user_params = pickle.load(f)

engine = create_engine('sqlite:///mosileno.sqlite')
DBSession.configure(bind=engine)

user = DBSession.query(User).filter_by(name=username).one()

top_topics = sorted(enumerate(user_params), key=operator.itemgetter(1), reverse=True)

for (t, _) in top_topics[:10]:
    with transaction.manager:
        tn = topics_tools.lda_topic_names[t]
        utn = UserTopicName(user.id, tn)
        DBSession.add(utn)

items = DBSession.query(Item)\
                 .join(Feed)\
                 .join(Subscription)\
                 .filter(Subscription.user == user.id)\
                 .all()

for item in items:
    with transaction.manager:
        print item.id
        text = topics_tools.tika(item.link)
        if text is None:
            score = 0
        else:
            a = utils.lemmatize(text)

            score = 0.0
            lda = topics_tools.lda_model
            for topicid, proba in lda[lda.id2word.doc2bow(a)]:
                score += proba * user_params[topicid]

        item_score = ItemScore(item.id, user.id, score)
        DBSession.add(item_score)
