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
from deform.widget import PasswordWidget

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

def tpl(request, **kwargs):
    """
    Fill in default values for template arguments.
    """
    args = dict(logged_in=authenticated_userid(request))
    return dict (kwargs.items() + args.items())

@view_config(route_name='home', renderer='templates/page.pt')
def view_test(request):
    return tpl(request, content='This is only a test')

class LoginSchema(Schema):
    login = SchemaNode(String())
    password = SchemaNode(String(), widget=PasswordWidget())

@view_config(route_name='login',
             renderer='templates/form.pt')
@forbidden_view_config(renderer='templates/form.pt')
class LoginView(FormView):
    schema=LoginSchema()
    buttons=('login',)

    def login_success(self, appstruct):
        login = appstruct['login']
        password = appstruct['password']
        if auth_correct(login, password):
            headers = remember(request, login)
            return HTTPFound(location = '/',
                             headers = headers)

    # pylint: disable=E0202
    def show(self, form):
        d = super(LoginView, self).show(form)
        return tpl(self.request, **d)

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.resource_url(request.context),
                     headers = headers)

class SignupSchema(LoginSchema):
    pass

@view_config(route_name ='signup',
        renderer='templates/form.pt'
        )
class SignupView(FormView):
    schema=SignupSchema()
    buttons=('signup',)

    def signup_success(self, appstruct):
        login = appstruct['login']
        password = appstruct['password']
        user = User(login, password)
        DBSession.add(user)
        return HTTPFound(location = '/')

    # pylint: disable=E0202
    def show(self, form):
        d = super(SignupView, self).show(form)
        return tpl(self.request, **d)

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
        return tpl(self.request, **d)
