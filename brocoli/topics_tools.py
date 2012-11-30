import pickle
#import requests
import numpy
import sys
from gensim import utils

LEMMATIZE= True
lda_model = None
topic_model_filename = 'topic-model/hn40%s.ldamodel'

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
        topicnames.append(ldaobject.id2word[bests[topicid][0]].split('/')[0] + "/" 
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
            topicnames[topicid] = ldaobject.id2word[bests[topicid][ind]].split('/')[0]
            break
        ind = 1
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
            if ind == 1:
                # if it's the second we keep the default
                break
            topicnames[topicid] = topicnames[topicid] + '/' + ldaobject.id2word[bests[topicid][ind]].split('/')[0]
            break
    return zip(range(ldaobject.num_topics), topicnames)

def manual_HN_topic_names(ldaobject):
    topicnames = ['' for i in range(ldaobject.num_topics)]
    if LEMMATIZE:
        if ldaobject.num_topics == 40:
            topicnames = ['facebook (social networks)',
                    'months',
                    'code',
                    'password',
                    'energy & transportation',
                    'files', # github, shift...
                    'economy', # money, market, banking
                    'SF/Bay area',
                    'domain names',
                    'twitter (social networks)',
                    'tech (& crunch)',
                    'online marketplace',
                    'microsoft',
                    'login/account',
                    'smartphones',
                    'programming (languages)',
                    'social news',
                    '', # datum, page, search, link, result
                    'design',
                    'response?', # re, re, lot, problem, better
                    'programming',
                    'online/social news',
                    'life',
                    'NYC',
                    'business',
                    'tech news',
                    'education',
                    'amazon',
                    'cloud',
                    'web dev',
                    '', # cs, image, thank, web, page
                    'OS',
                    'HN metadata', # points and votes
                    'wikipedia & web',
                    'months',
                    'RoR',
                    'patents law',
                    'video games',
                    '', # vote, zdnet, topic, search
                    'startups']
        else:
            pass # TODO HAND SELECTED TOPICS FOR HN LEMMATIZED 100 TOPICS
    else:
        topicnames = ['customer service',
                'market finance',
                'technological innovation',
                'server performance',
                'web frameworks',
                'patents law',
                'months',
                'cloud computing',
                'computer science',
                'web apps',
                'social web',
                '(human) languages',
                'free software',
                '', # HN metadata
                '', # user login junk
                'unix/linux (OS)',
                'tech news',
                'public relations', # review/conf/PR
                'space tech', # & light & energy
                'news business',
                'network security',
                'social networks',
                'video games',
                'linux (kernel)',
                'NYC',
                '', # art & opinion & tech & news & business
                'shoes',
                'design (web)',
                'academia',
                'laptops & tablets',
                'account/login', # login junk
                '', # foursquare?
                'social web',
                'sexes differences',
                'energy (science)',
                'SF/Bay area',
                'news (UK)',
                'login/password', # login/pw junk
                'spam?', # offensive / tumblr ?
                'code',
                'online shopping',
                'names', # just names...
                'globalization',
                'time',
                'months',
                '(human) languages',
                'publishing', # + privacy
                'email',
                'web sites',
                '', # junk
                'medecine',
                'tech news (Cnet)',
                'chips (hardware)',
                'life',
                'UK (Europe)',
                'social news (Reddit)',
                'Bloomberg',
                'cars',
                'startups',
                'responses', # re re try wrtie
                'music (clips)',
                'SEO',
                'government',
                'argumentation',
                '', # junk
                '', # junk
                'geek news',
                'news recommendation', # + email
                'developing countries',
                '', # junk
                'software development',
                'search engines',
                'social networks',
                'food',
                '', # junk
                'funding',
                '', # junk
                'books',
                'economy',
                'education',
                'sport news',
                'mobile phones',
                '', # junk
                'movies', # ???
                'questions',
                'data structures',
                'PG',
                'wikipedia',
                'html',
                'artificial intelligence', # machine learning human intelligence
                'news',
                'software',
                'thanks',
                'photos',
                'Apple',
                'browsers',
                'journals',
                '', # junk
                'programming languages',
                'money/pricing']

    topn = ldaobject.num_topics
    bests = []
    topic_probas = []
    for topicid in range(ldaobject.num_topics):
        topic = ldaobject.state.get_lambda()[topicid]
        topic /= topic.sum()
        topic_probas.append(topic)
        bests.append(numpy.argsort(topic)[::-1][:topn])
    for topicid in range(ldaobject.num_topics):
        best10 = bests[topicid][:10]
        beststrl = []
        if LEMMATIZE:
            beststrl = [(topic_probas[topicid][i], ldaobject.id2word[i].split('/')[0])
                    for i in best10] # to remove POS-tag ("VB" in "be/VB")
        else:
            beststrl = [(topic_probas[topicid][i], ldaobject.id2word[i]) for i in best10]
        beststr = ' + '.join(['%.3f*%s' % v for v in beststrl])
        print "topic #", topicid, " described by:", topicnames[topicid]
        print beststr
    return zip(range(ldaobject.num_topics), topicnames)


init_topic_model()
lda_topic_names = dict(manual_HN_topic_names(lda_model))


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
