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
from pyramid.renderers import (
    get_renderer,
    render,
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

import tasks

import opml
import itertools
import colander

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    User,
    Subscription,
    Item,
    Feed,
    Invitation,
    Vote,
    Signal
)

from .auth import (
    auth_correct,
    update_password,
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


def tpl(request, **kwargs):
    """
    Fill in default values for template arguments.
    """
    args = dict(logged_in=authenticated_userid(request))
    return dict(kwargs.items() + args.items())


@view_config(route_name='expandedview')
def view_expanded(request):
    return _templated_feeds_view('expandedview', request)


@view_config(route_name='home')
def view_home(request):
    return _templated_feeds_view('home', request)


def _templated_feeds_view(page_name, request):
    rsp = None
    logged_in = authenticated_userid(request)
    if not logged_in:
        rsp = render('page.mako',
                     tpl(request,
                         activetab=page_name,
                         content='Welcome !',
                         ),
                     request)
    else:
        data = view_myfeeds(request, page_name)
        rsp = render(page_name + '.mako', data, request)
    return Response(rsp)


class TemplatedFormView(FormView):
    """
    A subclass of Formview that fills the template parameters with tpl().

    It also displays self.errors and self.successes in alert boxes and sets the
    active tab if an 'activetab' class parameter exists.
    """

    def __init__(self, request):
        super(FormView, self).__init__()
        self.request = request
        self.errors = []
        self.successes = []

    def show(self, form):
        d = FormView.show(self, form)
        d['errors'] = self.errors
        d['successes'] = self.successes
        if hasattr(self, 'activetab'):
            d['activetab'] = self.activetab
        return tpl(self.request, **d)

    def failure(self, e):
        pass


class LoginSchema(colander.Schema):
    username = colander.SchemaNode(colander.String())
    password = colander.SchemaNode(colander.String(), widget=PasswordWidget())
    redir = colander.SchemaNode(colander.String(),
                                widget=HiddenWidget(),
                                missing='/')


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
        else:
            self.errors = ['Wrong username or password.']


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
        invite_code = colander.SchemaNode(colander.String(),
                                          title='Invitation code',
                                          missing='no code',
                                          )
    schema = SignupSchema()
    buttons = ('signup',)

    def before(self, form):
        if not self.request.registry.settings.get('invite_only', False):
            form.schema['invite_code'].widget = HiddenWidget()

    def signup_success(self, appstruct):
        needs_invite = self.request.registry.settings.get('invite_only', False)
        invite = DBSession.query(Invitation)\
                          .filter_by(code=appstruct['invite_code'])\
                          .first()
        if needs_invite and not invite:
            self.errors = ['Signup is disabled']
            return None
        if invite is not None:
            DBSession.delete(invite)
        login = appstruct['username']
        password = appstruct['password']
        user = User(login, password)
        DBSession.add(user)
        headers = remember(self.request, login)
        return HTTPFound(location='/',
                         headers=headers)


# TODO this leaks memory,
# See FileUploadTempStore on
# http://docs.pylonsproject.org/projects/deform/en/latest/interfaces.html
class MemoryTmpStore(dict):
    def preview_url(self, name):
        return None


@view_config(route_name='feedadd',
             renderer='form.mako',
             permission='edit',
             )
def view_feedadd(request):

    counter = itertools.count()

    class FeedAddSchema(colander.Schema):
        url = colander.SchemaNode(colander.String())
    form1 = Form(FeedAddSchema(),
                 buttons=('add',),
                 formid='form1',
                 counter=counter)

    def form1_success(request, appstruct):
        url = appstruct['url']
        tasks.import_feed(request, url)
        return 'Feed imported'

    class OPMLImportSchema(colander.Schema):
        opml = colander.SchemaNode(FileData(),
                                   widget=FileUploadWidget(MemoryTmpStore()))
    form2 = Form(OPMLImportSchema(),
                 buttons=('import',),
                 formid='form2',
                 counter=counter)

    def form2_success(request, appstruct):
        opml_file = appstruct['opml']
        opml_data = opml_file['fp']
        outline = opml.parse(opml_data)
        worklist = [e for e in outline]
        n = 0
        while worklist:
            element = worklist.pop(0)
            if hasattr(element, 'xmlUrl'):
                url = element.xmlUrl
                tasks.import_feed(request, url)
                n += 1
            else:
                worklist += element
        return '%d feeds imported' % n

    forms = [('form1', form1, form1_success),
             ('form2', form2, form2_success)
             ]

    html = []
    info = []
    js = set()
    css = set()
    for (_, form, _) in forms:
        resources = form.get_widget_resources()
        js |= set(resources['js'])
        css |= set(resources['css'])

    if 'import' in request.POST or 'add' in request.POST:
        posted_formid = request.POST['__formid__']
        for (formid, form, on_success) in forms:
            if formid == posted_formid:
                try:
                    controls = request.POST.items()
                    appstruct = form.validate(controls)
                    msg = on_success(request, appstruct)
                    info.append(msg)
                    html.append(form.render(appstruct))
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
    d = {'form': html,
         'info': info,
         'showmenu': True,
         'title': 'Import a source',
         'activetab': 'addsrc',
         'js_links': js,
         'css_links': css,
         }
    return tpl(request, **d)


def _view_items(request, user, items,
                activetab='home', activeview=None, manage=None):
    """
    Retrieve and display a list of feed items.

    Arguments
        request : the current request
        user    : the user currently logged in
        items   : the items to display, as a list of
                  (item, feed title)

    Keyword arguments
        activeview : the data-activeview value that will be set class=active
                     (default: highlight none)
        activetab  : same for active tab (in header)
                     (default: highlight home)
        manage     : a feedObj for which the "manage" links (unsubscribe only
                     so far) will be displayed

    Returns
        a dictionary meant to be rendered by home/expandedview.mako.
    """
    items = [(i, "collapse%d" % n, t) for (n, (i, t)) in enumerate(items)]
    feeds = DBSession.query(Feed)\
                     .join(Subscription)\
                     .filter(Subscription.user == user.id)\
                     .filter(Feed.title != None)

    return tpl(request,
               items=items,
               feeds=feeds,
               activeview=activeview,
               activetab=activetab,
               manage=manage,
               )


def view_myfeeds(request, activetab):
    me = authenticated_userid(request)
    user = DBSession.query(User).filter(User.name == me).one()
    items = DBSession.query(Item, Feed)\
                     .join(Feed)\
                     .join(Subscription)\
                     .filter(Subscription.user == user.id)\
                     .order_by(Item.date.desc())\
                     .limit(20)
    return _view_items(request, user, items,
                       activetab=activetab, activeview='all')


@view_config(route_name='feedview',
             renderer='expandedview.mako',
             permission='edit',
             )
def view_feed(request):
    slug = request.matchdict['slug']
    feedObj = DBSession.query(Feed).filter_by(slug=slug).one()
    feedid = feedObj.id
    me = authenticated_userid(request)
    user = DBSession.query(User).filter(User.name == me).one()

    # check that we're allowed
    subs = DBSession.query(Subscription)\
                    .filter(Subscription.user == user.id)\
                    .filter(Subscription.feed == feedid)\
                    .all()

    if len(subs) != 1:
        return tpl(request)  # Better than nothing. TODO add an error message

    items = DBSession.query(Item)\
                     .filter(Item.feed == subs[0].feed)\
                     .order_by(Item.date.desc())
    items = [(i, feedObj) for i in items]

    activeview = 'feed-%s' % slug

    return _view_items(request,
                       user,
                       items,
                       activeview=activeview,
                       manage=feedObj,
                       )


@view_config(route_name='profile',
             renderer='form.mako',
             permission='edit',
             )
class ProfileView(TemplatedFormView):

    class ProfileSchema(colander.Schema):
        oldpass = colander.SchemaNode(colander.String(),
                                      title='Old password',
                                      widget=PasswordWidget()
                                      )
        newpass = colander.SchemaNode(colander.String(),
                                      title='New password',
                                      widget=PasswordWidget()
                                      )

    schema = ProfileSchema()
    buttons = ('save',)

    activetab = 'profile'

    def save_success(self, appstruct):
        login = authenticated_userid(self.request)
        oldpass = appstruct['oldpass']
        newpass = appstruct['newpass']
        if update_password(login, oldpass, newpass):
            self.successes = ['Profile updated.']
        else:
            self.errors = ['The password you entered is incorrect.']


@view_config(route_name='about',
             renderer='about.mako')
def about(request):
    d = {'showmenu': True,
         'title': 'About',
         'activetab': ''
         }
    return tpl(request, **d)


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
        assert(action in Signal.sources_ok)

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

        vote = vote_map(action)
        vote_exists = DBSession.query(Vote)\
                               .filter_by(vote=vote,
                                          item=itemid,
                                          user=userid)\
                               .first()
        if vote and not vote_exists:
            DBSession.add(Vote(vote, itemid, userid))
        return Response(status_code=200)  # TODO refine
    except:
        return Response(status_code=500)  # TODO refine


@view_config(route_name='feedunsub',
             renderer='form.mako'
             )
class FeedUnsubscribeView(TemplatedFormView):
    class FeedUnsubscribeSchema(colander.Schema):
        feed_id = colander.SchemaNode(colander.Integer(),
                                      widget=HiddenWidget())

    schema = FeedUnsubscribeSchema()
    buttons = ('unsubscribe',)

    def appstruct(self):
        slug = self.request.matchdict['slug']
        feed = DBSession.query(Feed).filter_by(slug=slug).one()
        return {'feed_id': feed.id}

    def unsubscribe_success(self, appstruct):
        feed_id = appstruct['feed_id']
        feed = DBSession.query(Feed).get(feed_id)

        me = authenticated_userid(self.request)
        user = DBSession.query(User).filter_by(name=me).one()

        sub = DBSession.query(Subscription)\
                       .filter_by(user=user.id)\
                       .filter_by(feed=feed_id)\
                       .first()
        if sub:
            DBSession.delete(sub)
            msg = 'You unsubscribed from "%s"' % feed.title
            self.successes = [msg]
        else:
            self.errors = ['You are not subscribed to "%s"' % feed.title]
