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
from deform.widget import (
    PasswordWidget,
    FileUploadWidget,
    HiddenWidget,
)
from deform.schema import FileData
from urlparse import urlparse

from .tasks import fetch_title, import_feed

import opml

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    User,
    Subscription,
    Item,
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
    return dict(kwargs.items() + args.items())


@view_config(route_name='home', renderer='page.mako')
def view_home(request):
    return tpl(request, content='Welcome !')


class TemplatedFormView(FormView):
    """
    A subclass of Formview that fills the template parameters with tpl().
    """

    def show(self, form):
        d = FormView.show(self, form)
        return tpl(self.request, **d)


class LoginSchema(Schema):
    username = SchemaNode(String())
    password = SchemaNode(String(), widget=PasswordWidget())
    redir = SchemaNode(String(), widget=HiddenWidget(), missing='/')


@view_config(route_name='login',
             renderer='form.mako')
@forbidden_view_config(renderer='form.mako')
class LoginView(TemplatedFormView):
    schema = LoginSchema()
    buttons = ('login',)

    def appstruct(self):
        dest = urlparse(self.request.url)
        redir = dest.path
        if redir == '/login':
            redir = '/'
        return {'redir': redir}

    def login_success(self, appstruct):
        login = appstruct['username']
        password = appstruct['password']
        redir = appstruct['redir']
        if auth_correct(login, password):
            headers = remember(self.request, login)
            return HTTPFound(location=redir,
                             headers=headers)


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location=request.resource_url(request.context),
                     headers=headers)


@view_config(route_name='signup',
             renderer='form.mako'
             )
class SignupView(TemplatedFormView):
    class SignupSchema(LoginSchema):
        pass
    schema = SignupSchema()
    buttons = ('signup',)

    def signup_success(self, appstruct):
        login = appstruct['username']
        password = appstruct['password']
        user = User(login, password)
        DBSession.add(user)
        return HTTPFound(location='/')


@view_config(route_name='feedadd',
             renderer='form.mako',
             permission='edit',
             )
class FeedAddView(TemplatedFormView):
    class FeedSchema(Schema):
        url = SchemaNode(String())
    schema = FeedSchema()
    buttons = ('save',)

    def save_success(self, appstruct):
        url = appstruct['url']
        import_feed(self.request, url)


# TODO this leaks memory,
# See FileUploadTempStore on
# http://docs.pylonsproject.org/projects/deform/en/latest/interfaces.html
class MemoryTmpStore(dict):
    def preview_url(self, name):
        return None


@view_config(route_name='opmlimport',
             renderer='form.mako',
             permission='edit',
             )
class OPMLImportView(TemplatedFormView):
    class OPMLImportSchema(Schema):
        opml = SchemaNode(FileData(),
                          widget=FileUploadWidget(MemoryTmpStore()))
    schema = OPMLImportSchema()
    buttons = ('import',)

    def import_success(self, appstruct):
        opml_file = appstruct['opml']
        opml_data = opml_file['fp']
        outline = opml.parse(opml_data)
        worklist = [e for e in outline]
        n = 0
        while worklist:
            element = worklist.pop(0)
            if hasattr(element, 'xmlUrl'):
                url = element.xmlUrl
                import_feed(self.request, url)
                n += 1
            else:
                worklist += element
        msg = '%d feeds imported' % n
        return Response(msg)


@view_config(route_name='myfeeds',
             renderer='itemlist.mako',
             permission='edit',
             )
def view_myfeeds(request):
    me = authenticated_userid(request)
    user = DBSession.query(User).filter(User.name == me).one()
    items = DBSession.query(Item)\
                     .join(Feed)\
                     .join(Subscription)\
                     .filter(Subscription.user == user.id)\
                     .order_by(Item.date.desc())\
                     .limit(20)
    items = [(i, "collapse%d" % n) for (n, i) in enumerate(items)]
    return tpl(request, items=items)
