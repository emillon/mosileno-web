from pyramid.view import (
    view_config,
)

from .models import (
    DBSession,
    Signal,
    User,
    Vote,
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
    user = User.logged_in(request)
    if user is None:
        request.response_status = '401 Unauthorized'
        return {}
    userid = user.id
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


@view_config(route_name='voteget',
             renderer='json',
             )
def get_vote(request):
    """
    Input

        A (json) list of ids/data. Data can be anything you want.

            Ex:

                [{'id': 1, 'data': 'xx'},
                 {'id': 3, 'data': 'yy'},
                 {'id': 4, 'data': 'zz'}
                 ]

    Output

        The votes for these ids

            Ex:

                [{'id': 1, 'data': 'xx', 'vote': 1},
                 {'id': 3, 'data': 'yy', 'vote': 1},
                 {'id': 4, 'data': 'zz', 'vote': -1}
                 ]
    """
    data_in = request.json_body
    user = User.logged_in(request)

    def answer(x):
        vote = DBSession.query(Vote)\
                        .filter_by(user=user.id, item=x['id'])\
                        .first()
        res = 0
        if vote is not None:
            res = vote.value
        return {'id': x['id'],
                'data': x['data'],
                'vote': res
                }
    return [answer(x) for x in data_in]
