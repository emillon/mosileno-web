import pickle
from gensim import utils

def tokenize(text):
    return [token.encode('utf8') for token in utils.tokenize(text, lower=True, errors='ignore') if 2 <= len(token) <= 20 and not token.startswith('_')]

#if not utils.HAS_PATTERN: TODO
#    import sys
#    print >> sys.stderr, "FATAL ERROR:"
#    print >> sys.stderr, "Y U NO HAS PATTERN?"
#    sys.exit(-1) /TODO
#def lemmatize(text):
#    return utils.lemmatize(text)

lda_model = None

with open('topic-model/hn.ldamodel', 'r') as f:
    lda_model = pickle.load(f)
