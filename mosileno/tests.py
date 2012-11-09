import unittest
import transaction
import pyramid_celery
import urllib2

from mock import Mock

from StringIO import StringIO

from testproxy import TestProxy
from urlparse import urlparse

from pyramid import testing
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    User,
    Feed,
    Subscription,
    Item,
)

from .views import (
    LoginView,
    view_home,
    logout,
    SignupView,
    FeedAddView,
    OPMLImportView,
)

from .tasks import import_feed

PROXY_URL = 'localhost'
PROXY_PORT = 1478


class TestMyView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            alfred = User("alfred", "alfredo", workfactor=1)
            DBSession.add(alfred)
        self.config.testing_securitypolicy(userid='alfred', permissive=False)
        celery_settings = {'CELERY_ALWAYS_EAGER': True,
                           'CELERY_EAGER_PROPAGATES_EXCEPTIONS': True,
                           }
        celery_config = Mock()
        celery_config.registry = Mock()
        celery_config.registry.settings = celery_settings
        pyramid_celery.includeme(celery_config)
        proxies = {'http': '%s:%d' % (PROXY_URL, PROXY_PORT)}
        handler = urllib2.ProxyHandler(proxies)
        self.config.add_settings({'urllib2_handlers': [handler]})

    @classmethod
    def setUpClass(cls):
        html = """
        <html>
            <head>
                <link rel="alternate"
                      type="application/rss+xml"
                      title="RSS Title"
                      href="./rss.xml">
                </link>
            </head>
            <body>
            </body>
        <html>
        """
        html_noalt = """
        <html>
            <head>
            </head>
            <body>
            </body>
        <html>
        """
        feed = """
        <?xml version="1.0" encoding="utf-8"?>
        <rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
            <channel>
                <title>Feed title</title>
                <link>Feed link</link>
                <description>Feed description</description>
                <item>
                    <title>Title 1</title>
                    <link>Link 1</link>
                    <description>Description 1</description>
                </item>
                <item>
                    <title>Title 2</title>
                    <link>Link 2</link>
                    <description>Description 2</description>
                </item>
                <item>
                    <title>Title 3</title>
                    <link>Link 3</link>
                    <description>Description 3</description>
                </item>
            </channel>
        </rss>
        """
        routes = {'/page.html': html,
                  '/rss.xml': feed,
                  '/noalt.html': html_noalt,
                  }
        cls.proxy = TestProxy(routes, (PROXY_URL, PROXY_PORT))
        cls.proxy.start()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def _login_with(self, user):
        user['login'] = 'submit'
        request = testing.DummyRequest(user)
        lv = LoginView(request)()
        return lv

    def test_login_fail(self):
        user = dict(username="doesnotexist",
                    password="doesnotexist",
                    )
        lv = self._login_with(user)
        self.assertNotIsInstance(lv, HTTPFound)

    def test_login_ok(self):
        user = dict(username="alfred",
                    password="alfredo",
                    )
        lv = self._login_with(user)
        self.assertIsInstance(lv, HTTPFound)

    def test_logout(self):
        request = testing.DummyRequest()
        resp = logout(request)
        self.assertIsInstance(resp, HTTPFound)

    def test_signup(self):
        params = dict(username="michel",
                      password="michelo",
                      signup="submit",
                      )
        request = testing.DummyRequest(params)
        view = SignupView(request)
        resp = view()
        self.assertIsInstance(resp, HTTPFound)

    def test_addfeed(self):
        url = 'http://example.com/doesnotexist.xml'
        params = dict(url=url,
                      save='submit')
        request = testing.DummyRequest(params)
        view = FeedAddView(request)
        view()
        find_feed = DBSession.query(Feed).filter(Feed.url == url)
        count_f = find_feed.count()
        self.assertEqual(count_f, 1)
        feed_id = find_feed.one().id
        sub = DBSession.query(Subscription).get(feed_id)
        self.assertIsNotNone(sub)

    def test_importopml(self):
        opml = """<?xml version="1.0" encoding="UTF-8"?>
        <opml version="1.0">
            <head>
                <title>OPML feed example</title>
            </head>
            <body>
                <outline text="Feed A text" title="Feed A" type="rss"
                    xmlUrl="http://feeda.example.com/feed.xml"
                    htmlUrl="http://feeda.example.com/feed.xml"/>
                <outline text="Feed B text" title="Feed B" type="rss"
                    xmlUrl="http://feedb.example.com/feed.xml"
                    htmlUrl="http://feedb.example.com/feed.xml"/>
                </body>
            </opml>
        """
        upload = Mock()
        upload.file = StringIO(opml)
        upload.filename = 'opml.xml'
        params = {'opml': {'upload': upload}, 'import': 'submit'}
        request = testing.DummyRequest(post=params)
        view = OPMLImportView(request)
        response = view()
        self.assertIn('2 feeds imported', response.text)

    def test_import_deep(self):
        opml = """<?xml version="1.0" encoding="UTF-8"?>
        <opml version="1.0">
            <head>
                <title>OPML feed example</title>
            </head>
            <body>
                <outline title="Category A" text="Category A text">
                    <outline text="Feed A1 text" title="Feed A1" type="rss"
                        xmlUrl="http://feeda1.example.com/feed.xml"
                        htmlUrl="http://feeda1.example.com/feed.xml"/>
                    <outline text="Feed A2 text" title="Feed A2" type="rss"
                        xmlUrl="http://feeda2.example.com/feed.xml"
                        htmlUrl="http://feeda2.example.com/feed.xml"/>
                </outline>
                <outline title="Category B" text="Category B text">
                    <outline text="Feed B1 text" title="Feed B1" type="rss"
                        xmlUrl="http://feedb1.example.com/feed.xml"
                        htmlUrl="http://feedb1.example.com/feed.xml"/>
                    <outline text="Feed B2 text" title="Feed B2" type="rss"
                        xmlUrl="http://feedb2.example.com/feed.xml"
                        htmlUrl="http://feedb2.example.com/feed.xml"/>
                </outline>
                </body>
            </opml>
        """
        upload = Mock()
        upload.file = StringIO(opml)
        upload.filename = 'opml.xml'
        params = {'opml': {'upload': upload}, 'import': 'submit'}
        request = testing.DummyRequest(post=params)
        view = OPMLImportView(request)
        response = view()
        self.assertIn('4 feeds imported', response.text)

    def test_discover(self):
        url = 'http://example.com/page.html'
        request = testing.DummyRequest()
        fid = import_feed(request, 'http://example.com/page.html')
        items = DBSession.query(Item).filter(Item.feed == fid).all()
        self.assertEqual(len(items), 3)

    def test_discover_noalt(self):
        url = 'http://example.com/page.html'
        request = testing.DummyRequest()
        fid = import_feed(request, url)
        # Should be deleted
        feeds = DBSession.query(Feed).filter(Feed.url == url).all()
        self.assertEqual(len(feeds), 0)


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from mosileno import main
        params = {'sqlalchemy.url': 'sqlite://',
                  'mako.directories': 'mosileno:templates',
                  'pyramid.includes': 'pyramid_deform',
                  }
        app = main({}, **params)
        engine = DBSession.get_bind(mapper=None)
        Base.metadata.create_all(engine)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        DBSession.remove()

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertIn('Welcome', res.body)

    def _register_user(self, user, password):
        res = self.testapp.get('/signup')
        form = res.form
        form['username'] = user
        form['password'] = password
        return form.submit('signup')

    def _login_helper(self, username, password, res):
        form = res.form
        form['username'] = username
        form['password'] = password
        return form.submit('login')

    def _logout(self):
        return self.testapp.get('/logout')

    def test_redirect(self, url=None, redir_url=None):
        """
        When going to a URL where auth is required, the login form should
        redirect to this page and not /.
        """
        username = 'alfred'
        password = 'alfred'
        self._register_user(username, password)
        self._logout()
        if url is None:
            url = '/feed/add'
        if redir_url is None:
            redir_url = url
        res = self.testapp.get(url)
        self.assertIn('Password', res.body)
        res = self._login_helper(username, password, res)
        self.assertEqual(res.status_code, 302)
        dest = urlparse(res.location)
        self.assertEqual(dest.path, redir_url)

    def test_redirect_login(self):
        """
        When logging in through /login, redirect to /
        """
        self.test_redirect(url='/login', redir_url='/')

    def test_myfeeds(self):
        """
        When accessing 'my feeds':
          - redirect to login if not authed, login and in all cases
          - gives the links defined in setUpClass
        """
        res = self.testapp.get('/feeds/my')
        if 'Login' in res.body:
            self.assertIn('Password', res.body)
            username = 'alfred'
            password = 'alfred'
            res = self._register_user(username, password)
            self.assertEqual(res.status_code, 302)
        if 'Logout' in res.body:
            self.assertIn('Title 1', res.body)

    def test_login_on_signup(self):
        res = self._register_user('robert', 'robert')
        res = res.follow()
        self.assertIn('Logout', res.body)
        self.assertIn('robert', res.body)
