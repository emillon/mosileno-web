from pyramid.response import Response
from pyramid.view import (
        view_config,
        forbidden_view_config,
        )
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    MyModel,
    )

from .auth import auth_correct

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    try:
        one = DBSession.query(MyModel).filter(MyModel.name=='one').first()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'one':one, 'project':'mosileno'}

@view_config(route_name='test', renderer='templates/page.pt')
def view_test(request):
    return {'content': 'This is only a test'}

@view_config(route_name='authtest',
        renderer='templates/page.pt',
        permission='testperm')
def view_authtest(request):
    return {'content': 'Auth test'}

@view_config(route_name='login',
             renderer='templates/login.pt')
@forbidden_view_config(renderer='templates/login.pt')
def view_login(request):
    login_url = request.resource_url(request.context, 'login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        if auth_correct(login, password):
            headers = remember(request, login)
            return HTTPFound(location = came_from,
                             headers = headers)
        message = 'Failed login'

    return dict(
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        login = login,
        password = password,
        )

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_mosileno_db" script
    to initialize your database tables.  Check your virtual 
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

