import pickle
import sys
import topics_tools
from gensim import utils
from sqlalchemy import create_engine

from mosileno.models import *

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

items = DBSession.query(Item).all()

for item in items:
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
