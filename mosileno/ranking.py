"""
Ranking functions (reddit-style, HN-style, etc)
"""

import datetime
import math

from models import *

from pyramid.security import authenticated_userid


def norm_date(dt):
    """
    Replace a None datetime by an epoch.

    Not perfect I guess ! -- EM
    """
    epoch = datetime.datetime(2012, 12, 27)
    if dt is None:
        return epoch
    return dt


def reddit(request, item):
    date = norm_date(item.date)
    me = authenticated_userid(request)
    user = DBSession.query(User).filter(User.name == me).one()
    ups = DBSession.query(Vote)\
                   .filter_by(user=user.id,
                              item=item.id,
                              value=1,
                              )\
                   .count()
    downs = DBSession.query(Vote)\
                     .filter_by(user=user.id,
                                item=item.id,
                                value=-1,
                                )\
                     .count()
    score = ups - downs
    order = math.log(max(abs(score), 1), 10)
    sign = math.copysign(1, score)
    unix_epoch = datetime.datetime(1970, 1, 1)
    td = date - unix_epoch
    seconds = td.days * 86400 + td.seconds +\
        (float(td.microseconds) / 1000000) - 1134028003
    score = round(order + sign * seconds / 45000, 7)
    return score


def clover(user, item):
    itemscore = DBSession.query(ItemScore)\
                         .filter_by(user=user.id, item=item.id)\
                         .first()
    if itemscore is None:
        return 0
    return itemscore.score
