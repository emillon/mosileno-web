from pyramid.response import Response
from pyramid.view import (
    view_config,
    forbidden_view_config,
    notfound_view_config,
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

import colander
import deform
import itertools
import opml
import urlparse

import ranking
import tasks

from .models import *

from .auth import (
    auth_correct,
    update_password,
)


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
        user = DBSession.query(User).filter(User.name == logged_in).one()
        data = view_myfeeds(request, page_name, limit=30)
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
    password = colander.SchemaNode(colander.String(),
                                   widget=deform.widget.PasswordWidget())
    redir = colander.SchemaNode(colander.String(),
                                widget=deform.widget.HiddenWidget(),
                                missing='/')


@view_config(route_name='login',
             renderer='form.mako')
@forbidden_view_config(renderer='form.mako')
class LoginView(TemplatedFormView):
    schema = LoginSchema()
    buttons = ('login',)

    def appstruct(self):
        dest = urlparse.urlparse(self.request.url)
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
            form.schema['invite_code'].widget = deform.widget.HiddenWidget()

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


def file_upload_widget():
    # TODO this leaks memory,
    # See FileUploadTempStore on
    # http://docs.pylonsproject.org/projects/deform/en/latest/interfaces.html
    class MemoryTmpStore(dict):
        def preview_url(self, name):
            return None

    return deform.widget.FileUploadWidget(MemoryTmpStore())


@view_config(route_name='feedadd',
             renderer='addsrc.mako',
             permission='edit',
             )
def view_feedadd(request):

    counter = itertools.count()

    class FeedAddSchema(colander.Schema):
        url = colander.SchemaNode(colander.String())

    form1 = deform.Form(FeedAddSchema(),
                        buttons=('add',),
                        formid='form1',
                        counter=counter)

    def form1_success(request, appstruct):
        url = appstruct['url']
        tasks.import_feed(request, url)
        return 'Feed imported'

    class OPMLImportSchema(colander.Schema):
        opml = colander.SchemaNode(deform.schema.FileData(),
                                   widget=file_upload_widget())
    form2 = deform.Form(OPMLImportSchema(),
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

    class RedditImportSchema(colander.Schema):
        subreddit = colander.SchemaNode(colander.String())

    form3 = deform.Form(RedditImportSchema(),
                        buttons=('connect',),
                        formid='form3',
                        counter=counter)

    def form3_success(request, appstruct):
        subreddit = appstruct['subreddit']
        url = 'http://www.reddit.com/r/%s.rss' % subreddit
        tasks.import_feed(request, url)
        return 'You are now connected to /r/%s' % subreddit

    forms = [('form1', form1, form1_success),
             ('form2', form2, form2_success),
             ('form3', form3, form3_success),
             ]

    html = []
    info = []
    js = set()
    css = set()
    for (_, form, _) in forms:
        resources = form.get_widget_resources()
        js |= set(resources['js'])
        css |= set(resources['css'])

    is_submitted = False
    for (_, form, _) in forms:
        if form.buttons[0].name in request.POST:
            is_submitted = True

    if is_submitted:
        posted_formid = request.POST['__formid__']
        for (formid, form, on_success) in forms:
            if formid == posted_formid:
                try:
                    controls = request.POST.items()
                    appstruct = form.validate(controls)
                    msg = on_success(request, appstruct)
                    info.append(msg)
                    html.append(form.render(appstruct))
                except deform.ValidationFailure as e:
                    # the submitted values could not be validated
                    html.append(e.render())
            else:
                html.append(form.render())
    else:
        for (_, form, _) in forms:
            html.append(form.render())

    # values passed to template for rendering
    d = {'form_rss': html[0],
         'form_opml': html[1],
         'form_reddit': html[2],
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
    topics = DBSession.query(UserTopicName)\
                      .filter_by(user=user.id)\
                      .all()

    def captopics(topicname):
        if topicname != '' and topicname[0].islower():
            return topicname.capitalize()
        else:
            return topicname
    topics = [captopics(t.topicname) for t in topics]

    def topics_for(item):
        tns = DBSession.query(ItemTopicName)\
                       .filter_by(item=item.id)\
                       .all()
        tns = [captopics(tn.topicname) for tn in tns if tn.topicname]
        return ', '.join(tns)

    def score_for(item):
        its = DBSession.query(ItemScore)\
                       .filter_by(item=item.id, user=user.id)\
                       .first()
        if its:
            score = 10000 * its.score
        else:
            score = 0
        return int((score / 1700) * 100)

    return tpl(request,
               items=items,
               feeds=feeds,
               topics=topics,
               activeview=activeview,
               activetab=activetab,
               manage=manage,
               score_for=score_for,
               topics_for=topics_for,
               )


def view_myfeeds(request, activetab, limit=20):
    me = authenticated_userid(request)
    user = DBSession.query(User).filter(User.name == me).one()
    items = DBSession.query(Item, Feed)\
                     .join(Feed)\
                     .join(Subscription)\
                     .filter(Subscription.user == user.id)\
                     .order_by(Item.date.desc())\
                     .all()
    rank = lambda (i, _): ranking.clover(request, i)
    items.sort(key=rank, reverse=True)  # Highest scores first
    items = items[:limit]
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

    if len(subs) == 0:
        return tpl(request,
                   errors=['You are not subscribed to this feed'],
                   items=[],
                   feeds=[],
                   topics=[],
                   )

    items = DBSession.query(Item)\
                     .filter(Item.feed == subs[0].feed)\
                     .order_by(Item.date.desc())
    items = [(i, feedObj) for i in items]

    activeview = 'feed-%s' % slug

    return _view_items(request,
                       user,
                       items,
                       activetab='expandedview',
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
                                      widget=deform.widget.PasswordWidget()
                                      )
        newpass = colander.SchemaNode(colander.String(),
                                      title='New password',
                                      widget=deform.widget.PasswordWidget()
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


@view_config(route_name='contact',
             renderer='page.mako')
def contact(request):
    msg = 'For any inquiries, please email etienne <at> cloverfeed <dot> com.'
    return tpl(request, content=msg)


@view_config(route_name='feedunsub',
             renderer='form.mako'
             )
class FeedUnsubscribeView(TemplatedFormView):
    class FeedUnsubscribeSchema(colander.Schema):
        feed_id = colander.SchemaNode(colander.Integer(),
                                      widget=deform.widget.HiddenWidget())

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


@notfound_view_config(renderer='page.mako')
def notfound(request):
    msg = """
    Oops, 404 ! Unable to find this page. If you think this is a bug, please
    report it using the "Report a bug" link below.
    """
    return tpl(request, content=msg)
