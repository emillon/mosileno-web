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
from deform import (
    Form,
    ValidationFailure,
)
from urlparse import urlparse

from .tasks import fetch_title, import_feed

import opml
import itertools

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
        headers = remember(self.request, login)
        return HTTPFound(location='/',
                         headers=headers)

class FeedAddSchema(Schema):
    url = SchemaNode(String())

def feed_add_success(request, appstruct):
    url = appstruct['url']
    import_feed(request, url)

class FeedAddView(TemplatedFormView):
    schema = FeedAddSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        return feed_add_success(self.request, appstruct)

# TODO this leaks memory,
# See FileUploadTempStore on
# http://docs.pylonsproject.org/projects/deform/en/latest/interfaces.html
class MemoryTmpStore(dict):
    def preview_url(self, name):
        return None

class OPMLImportSchema(Schema):
    opml = SchemaNode(FileData(),
                      widget=FileUploadWidget(MemoryTmpStore()))

def opml_import_success(request, appstruct):
    opml_file = appstruct['opml']
    opml_data = opml_file['fp']
    outline = opml.parse(opml_data)
    worklist = [e for e in outline]
    n = 0
    while worklist:
        element = worklist.pop(0)
        if hasattr(element, 'xmlUrl'):
            url = element.xmlUrl
            import_feed(request, url)
            n += 1
        else:
            worklist += element
    msg = '%d feeds imported' % n
    return Response(msg)

class OPMLImportView(TemplatedFormView):
    schema = OPMLImportSchema()
    buttons = ('import',)

    def import_success(self, appstruct):
        return opml_import_success(self.request, appstruct)

@view_config(route_name='feedadd',
             renderer='form.mako',
             permission='edit',
             )
def view_feedadd(request):

    counter= itertools.count()

    form1 = Form(FeedAddSchema(), buttons=('add',), formid='form1', counter=counter)
    form1_success = feed_add_success
    form2 = Form(OPMLImportSchema(), buttons=('import',), formid='form2', counter=counter)
    form2_success = opml_import_success

    forms = [('form1', form1, form1_success),
             ('form2', form2, form2_success)
             ]

    html = []
    captured = None

    if 'import' in request.POST or 'add' in request.POST:
        posted_formid = request.POST['__formid__']
        for (formid, form, on_success) in forms:
            if formid == posted_formid:
                try:
                    controls = request.POST.items()
                    appstruct = form.validate(controls)
                    html.append(form.render(appstruct))
                    on_success(request, appstruct)
                except ValidationFailure as e:
                    # the submitted values could not be validated
                    html.append(e.render())
            else:
                html.append(form.render())
    else:
        for (_, form, _) in forms:
            html.append(form.render())

    html = ''.join(html)

    # values passed to template for rendering
    d = {
        'form':html,
        'captured':repr(captured),
        'showmenu':True,
        'title':'Multiple Forms on the Same Page',
        }
    return tpl(request, **d)

def _view_items(request, user, items, activelink=None):
    """
    Retrieve and display a list of feed items.

    Arguments
        request : the current request
        user    : the user currently logged in
        items   : the items to display

    Keyword arguments
        activelink : a function to set class=active
                     (returns a boolean)
                     (default: highlight none)

    Returns
        a dictionary meant to be rendered by itemlist.mako.
    """
    items = [(i, "collapse%d" % n) for (n, i) in enumerate(items)]
    feeds = DBSession.query(Feed)\
                     .join(Subscription)\
                     .filter(Subscription.user == user.id)
    if activelink is None:
        activelink = lambda s: False

    def activestring(s):
        if activelink(s):
            return 'active'
        else:
            return ''
    return tpl(request, items=items, feeds=feeds, activelink=activestring)


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

    def activelink(s):
        return s == 'all'
    return _view_items(request, user, items, activelink=activelink)


@view_config(route_name='feedview',
             renderer='itemlist.mako',
             permission='edit',
             )
def view_feed(request):
    feedid = request.matchdict['feedid']
    me = authenticated_userid(request)
    user = DBSession.query(User).filter(User.name == me).one()

    # check that we're allowed
    subs = DBSession.query(Subscription)\
                    .filter(Subscription.user == user.id)\
                    .filter(Subscription.feed == feedid)\
                    .all()

    if len(subs) != 1:
        return tpl(request)  # Better than nothing. TODO add an error message

    items = DBSession.query(Item).filter(Item.feed == subs[0].feed)

    def activelink(s):
        return s == 'feed%s' % feedid

    return _view_items(request, user, items, activelink=activelink)
