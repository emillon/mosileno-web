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
from deform.widget import PasswordWidget, FileUploadWidget
from deform.schema import FileData

from celery.task import task

import feedparser
import transaction
import opml

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    MyModel,
    User,
    Feed,
    Subscription,
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
def view_home(request):
    return tpl(request, content='Welcome !')

class TemplatedFormView(FormView):
    """
    A subclass of Formview that fills the template parameters with tpl().
    """

    # pylint: disable=E0202
    def show(self, form):
        d = FormView.show(self, form)
        return tpl(self.request, **d)

class LoginSchema(Schema):
    username = SchemaNode(String())
    password = SchemaNode(String(), widget=PasswordWidget())

@view_config(route_name='login',
             renderer='templates/form.pt')
@forbidden_view_config(renderer='templates/form.pt')
class LoginView(TemplatedFormView):
    schema=LoginSchema()
    buttons=('login',)

    def login_success(self, appstruct):
        login = appstruct['username']
        password = appstruct['password']
        if auth_correct(login, password):
            headers = remember(self.request, login)
            return HTTPFound(location = '/',
                             headers = headers)

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
class SignupView(TemplatedFormView):
    schema=SignupSchema()
    buttons=('signup',)

    def signup_success(self, appstruct):
        login = appstruct['username']
        password = appstruct['password']
        user = User(login, password)
        DBSession.add(user)
        return HTTPFound(location = '/')

class FeedSchema(Schema):
    url = SchemaNode(String())

@view_config(route_name='feedadd',
        renderer='templates/form.pt',
        permission='edit',
        )
class FeedAddView(TemplatedFormView):
    schema=FeedSchema()
    buttons = ('save',)

    def save_success(self, appstruct):
        url = appstruct['url']
        import_feed(self.request, url)

def import_feed(request, url):
    feed = Feed(url)
    DBSession.add(feed)
    me = authenticated_userid(request)
    user = DBSession.query(User).filter(User.name==me).one()
    sub = Subscription(user, feed)
    DBSession.add(sub)
    fetch_title.delay(feed.id)

@task
def fetch_title(feed_id):
    feedObj = DBSession.query(Feed).get(feed_id)
    if feedObj is None:
        raise fetch_title.retry(countdown=3)
    feed = feedparser.parse(feedObj.url)
    feedObj.title = feed.feed.title
    transaction.commit()

# TODO this leaks memory :
# http://docs.pylonsproject.org/projects/deform/en/latest/interfaces.html#deform.interfaces.FileUploadTempStore
class MemoryTmpStore(dict):
    def preview_url(self, name):
        return None

class OPMLImportSchema(Schema):
    opml = SchemaNode(FileData(), widget=FileUploadWidget(MemoryTmpStore()))

@view_config(route_name='opmlimport',
        renderer='templates/form.pt',
        permission='edit',
        )
class OPMLImportView(TemplatedFormView):
    schema = OPMLImportSchema()
    buttons = ('import',)

    def import_success(self, appstruct):
        opml_file = appstruct['opml']
        opml_data = opml_file['fp']
        outline = opml.parse(opml_data)
        for feed in outline:
            url = feed.xmlUrl
            import_feed(self.request, url)
        msg = '%d feeds imported' % len(outline)
        return Response(msg)
