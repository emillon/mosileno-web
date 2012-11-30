import pickle
import requests
import numpy
import sys
from gensim import utils

LEMMATIZE= False
lda_model = None
topic_model_filename = 'topic-model/hn%s.ldamodel'

def init_topic_model():
    " Necessary spaghetti code to fall back on models "
    global lda_model, topic_model_filename, LEMMATIZE
    if utils.HAS_PATTERN:
        LEMMATIZE = True # we try and use pattern:
        # here we can change if we want to not use pattern and just tokenize
    else:
        print >> sys.stderr, "WARNING: you don't have the `pattern` library"
    if LEMMATIZE:
        try:
            with open((topic_model_filename % '_lemmatized'), 'r') as testf: pass
            topic_model_filename = (topic_model_filename % '_lemmatized')
        except IOError:
            LEMMATIZE = False
            print >> sys.stderr, "WARNING: You don't have the lemmatized model, it's bad!"
    if not LEMMATIZE:
        print >> sys.stderr, "WARNING: falling back to using the tokenized model..."
        topic_model_filename = (topic_model_filename % '')
    try:
        with open(topic_model_filename, 'r') as f:
            lda_model = pickle.load(f)
        print "*** Loaded topic model", topic_model_filename, "***"
    except IOError:
        print >> sys.stderr, ("ERROR: topic model %s inexistent or corrupted"
                % topic_model_filename)
        sys.exit(-1)


def topic_names(ldaobject):
    """ 
    Badly written heuristic which founds one or two words to describe a 
    topic. Returns a list of couples [(topicid, topicdescription)]
    """
    global LEMMATIZE
    topn = ldaobject.num_topics # should perhaps be less? 10?
    bests = []
    topicnames = []
    for topicid in range(ldaobject.num_topics):
        topic = ldaobject.state.get_lambda()[topicid]
        topic /= topic.sum()
        bests.append(numpy.argsort(topic)[::-1][:topn])
    for topicid in range(ldaobject.num_topics):
        topicnames.append(ldaobject.id2word[bests[topicid][0]].split('/')[0] + " " 
                + ldaobject.id2word[bests[topicid][1]].split('/')[0])
        ind = 0
        while ind < topn:
            contsearch = False
            # we seek the word bests[topicid][ind] in the bests words
            # for others topic
            for i,wl in enumerate(bests):
                if i == topicid:
                    continue
                if bests[topicid][ind] in wl:
                    # if we found bests[topicid][ind] in other topics' bests
                    # words, we try and find a more discrimining word
                    ind += 1
                    contsearch = True
                    break
            if contsearch:
                continue
            # here we are not "contsearch"ing, so we have found a discriming
            # word as bests[topicid][ind]:
            if ind == 0:
                # if it's the first we keep the default
                break
            topicnames[topicid] = ldaobject.id2word[bests[topicid][ind]].split('/')[0]
            break
        best10 = bests[topicid][:10]
    return zip(range(ldaobject.num_topics), topicnames)

_lda_topic_names = None  # Lazily loaded

init_topic_model()
lda_topic_names = dict(topic_names(lda_model))

def parse(text):
    def tokenize(text):
        return [token.encode('utf8') for token in utils.tokenize(text, lower=True, errors='ignore') if 2 <= len(token) <= 20 and not token.startswith('_')]
    global LEMMATIZE
    if LEMMATIZE:
        return utils.lemmatize(text)
    else:
        return tokenize(text)


def tika(url):
    rsp = requests.get('http://localhost:9998/', params={'doc': url})
    if 'retval' not in rsp.json:
        return None
    return rsp.json['retval']
