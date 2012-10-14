from pyramid.response import Response
from pyramid.view import (
        view_config,
        forbidden_view_config,
        )
from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
        remember,
        forget,
        authenticated_userid
        )
from pyramid_deform import FormView
from pyramid.renderers import get_renderer
from colander import (
        Schema,
        SchemaNode,
        String,
        )

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    MyModel,
    User,
    Feed,
    )

from .auth import auth_correct

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

@view_config(route_name='home', renderer='templates/page.pt')
def view_test(request):
    return dict(content='This is only a test',
                logged_in=authenticated_userid(request)
               )

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
        logged_in = authenticated_userid(request)
        )

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.resource_url(request.context),
                     headers = headers)

@view_config(route_name ='signup',
        renderer='templates/signup.pt'
        )
def view_signup(request):
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        user = User(login, password)
        DBSession.add(user)
        return HTTPFound(location = '/')
    return dict(
        url = request.application_url + '/signup',
        logged_in = authenticated_userid(request)
        )

class FeedSchema(Schema):
    url = SchemaNode(String())

@view_config(route_name='feedadd',
        renderer='templates/form.pt'
        )
class FeedAddView(FormView):
    schema=FeedSchema()
    buttons = ('save',)

    # pylint: disable=E0202
    def appstruct(self):
        request = self.request
        return dict()

    def save_success(self, appstruct):
        url = appstruct['url']
        feed = Feed(url)
        DBSession.add(feed)

    # pylint: disable=E0202
    def show(self, form):
        d = super(FeedAddView, self).show(form)
        d['logged_in'] = authenticated_userid(self.request)
        return d
