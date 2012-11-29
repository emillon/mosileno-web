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

@view_config(route_name='signal',
             renderer='json',
             )
def signal(request):
    def vote_map(vote_str):
        if vote_str == 'linkup':
            return 1
        elif vote_str == 'linkdown':
            return -1
        return 0

    source = request.POST['source']
    assert(source in Signal.sources_ok)

    action = request.POST['action']
    assert(action in Signal.actions_ok)

    itemid = request.POST['item']
    me = authenticated_userid(request)
    if me is None:
        request.response_status = '401 Unauthorized'
        return {}
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
    return {}  # TODO refine
