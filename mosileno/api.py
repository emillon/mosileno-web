from pyramid.view import (
    view_config,
)

from .models import (
    DBSession,
    Signal,
    User,
    Vote,
)

from pyramid.security import (
    authenticated_userid
)
from pyramid.response import Response

@view_config(route_name='signal')
def signal(request):
    def vote_map(vote_str):
        if vote_str == 'linkup':
            return 1
        elif vote_str == 'linkdown':
            return -1
        return 0

    try:
        source = request.POST['source']
        assert(source in Signal.sources_ok)

        action = request.POST['action']
        assert(action in Signal.actions_ok)

        itemid = request.POST['item']
        me = authenticated_userid(request)
        if me is None:
            return Response(status_code=401)  # Unauthorized
        userid = DBSession.query(User).filter_by(name=me).all()[0].id
        signal_exists = DBSession.query(Signal)\
                                 .filter_by(action=action,
                                            item=itemid,
                                            user=userid)\
                                 .first()
        if not signal_exists:
            DBSession.add(Signal(source, action, itemid, userid))

        value = vote_map(action)
        vote_exists = DBSession.query(Vote)\
                               .filter_by(value=value,
                                          item=itemid,
                                          user=userid)\
                               .first()
        if value and not vote_exists:
            vote = Vote(value, itemid, userid)
            DBSession.add(vote)
        return Response(status_code=200)  # TODO refine
    except AssertionError:
        return Response(status_code=500)  # TODO refine
