import unittest
import transaction
import pyramid_celery
import urllib2

from mock import Mock

from StringIO import StringIO

from urlparse import urlparse

from pyramid import testing
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import engine_from_config
from httpretty import HTTPretty, httprettified

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
    view_feedadd,
)

from .tasks import import_feed


DOCS = {'feed': """<?xml version="1.0" encoding="utf-8"?>
             <rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
                 <channel>
                     <title>Feed title</title>
                     <link>Feed link</link>
                     <description>Feed description</description>
                     <item>
                         <title>Title 1</title>
                         <link>Link 1</link>
                         <guid>GUID 1</guid>
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
             """,
        'page': """
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
            """,
        'opml': """<?xml version="1.0" encoding="UTF-8"?>
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
            """,
        'opml_deep': """<?xml version="1.0" encoding="UTF-8"?>
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
            """,
        }


class TestMyView(unittest.TestCase):
    def setUp(self):
        settings = {'mako.directories': 'mosileno:templates'}
        self.config = testing.setUp(settings=settings)
        self.config.add_static_view('static', 'mosileno:static')
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

    def _signup(self, username, password):
        params = dict(username=username,
                      password=password,
                      signup="submit",
                      )
        request = testing.DummyRequest(params)
        view = SignupView(request)
        resp = view()
        return resp

    def test_signup(self):
        resp = self._signup("michel", "michelo")
        self.assertIsInstance(resp, HTTPFound)

    @httprettified
    def test_addfeed(self):
        url = 'http://example.com/doesnotexist.xml'
        HTTPretty.register_uri(HTTPretty.GET, url,
                               body=DOCS['feed'],
                               content_type="text/html")
        params = {'url': url,
                  'add': 'submit',
                  '__formid__': 'form1',
                  }
        request = testing.DummyRequest(params)
        view_feedadd(request)
        find_feed = DBSession.query(Feed).filter(Feed.url == url)
        count_f = find_feed.count()
        self.assertEqual(count_f, 1)
        feed_id = find_feed.one().id
        sub = DBSession.query(Subscription).get(feed_id)
        self.assertIsNotNone(sub)

    def _opml(self, opml, urls, feed):
        for u in urls:
            HTTPretty.register_uri(HTTPretty.GET, u,
                                   body=feed,
                                   content_type='application/rss+xml')
        upload = Mock()
        upload.file = StringIO(opml)
        upload.filename = 'opml.xml'
        params = {'opml': {'upload': upload},
                  'import': 'submit',
                  '__formid__': 'form2',
                  }
        request = testing.DummyRequest(post=params)
        response = view_feedadd(request)
        return response

    @httprettified
    def test_importopml(self):
        urls = ['http://feeda.example.com/feed.xml',
                'http://feedb.example.com/feed.xml']
        response = self._opml(DOCS['opml'], urls, DOCS['feed'])
        self.assertIn('2 feeds imported', response['info'])

    @httprettified
    def test_import_deep(self):
        urls = ["http://feeda1.example.com/feed.xml",
                "http://feeda2.example.com/feed.xml",
                "http://feedb1.example.com/feed.xml",
                "http://feedb2.example.com/feed.xml",
                ]
        response = self._opml(DOCS['opml_deep'], urls, DOCS['feed'])
        self.assertIn('4 feeds imported', response['info'])

    @httprettified
    def test_discover(self):
        url = 'http://example.com/page.html'
        HTTPretty.register_uri(HTTPretty.GET, url,
                               body=DOCS['page'],
                               content_type="text/html")
        HTTPretty.register_uri(HTTPretty.GET, url,
                               body=DOCS['feed'],
                               content_type='application/rss+xml')
        request = testing.DummyRequest()
        fid = import_feed(request, url)
        items = DBSession.query(Item).filter(Item.feed == fid).all()
        self.assertEqual(len(items), 3)

    @httprettified
    def test_discover_noalt(self):
        url = 'http://example.com/noalt.html'
        html = """
        <html>
            <head>
            </head>
            <body>
            </body>
        <html>
        """
        HTTPretty.register_uri(HTTPretty.GET, url,
                               body=html,
                               content_type="text/html")
        request = testing.DummyRequest()
        fid = import_feed(request, url)
        # Should be deleted
        feeds = DBSession.query(Feed).filter(Feed.url == url).all()
        self.assertEqual(len(feeds), 0)

    @httprettified
    def test_add_twice(self):
        url = "http://feeda1.example.com/feed.xml"
        HTTPretty.register_uri(HTTPretty.GET, url,
                               body=DOCS['feed'],
                               content_type='application/rss+xml')
        request = testing.DummyRequest()
        fid1 = import_feed(request, url)
        fid2 = import_feed(request, url)
        self.assertEqual(fid1, fid2)
        feeds = DBSession.query(Feed).filter(Feed.url == url).all()
        self.assertEqual(len(feeds), 1)

    @httprettified
    def test_subscribe_existing(self):
        url = "http://feeda1.example.com/feed.xml"
        HTTPretty.register_uri(HTTPretty.GET, url,
                               body=DOCS['feed'],
                               content_type='application/rss+xml')

        request = testing.DummyRequest()
        fid = import_feed(request, url)

        self._signup('miguel', 'miguel')
        self.config.testing_securitypolicy(userid='miguel', permissive=False)

        request = testing.DummyRequest()
        fid2 = import_feed(request, url)

        self.assertEqual(fid, fid2)

        def sub_between(username, feed_id):
            user = DBSession.query(User).filter_by(name=username).one()
            sub = DBSession.query(Subscription)\
                           .filter_by(user=user.id)\
                           .filter_by(feed=feed_id)\
                           .first()
            return sub

        self.assertIsNotNone(sub_between('alfred', fid))
        self.assertIsNotNone(sub_between('miguel', fid))


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from mosileno import main
        params = {'sqlalchemy.url': 'sqlite://',
                  'mako.directories': 'mosileno:templates',
                  'pyramid.includes': ['pyramid_deform',
                                       'pyramid_tm',
                                       ],
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

    def test_root(self):
        """
        Test root route (/)

        On homepage :
          - Display a landing page (welcome !)
          - Display a login link
        """
        res = self.testapp.get('/')
        self.assertIn('Welcome !', res.body)
        self.assertIn('Login', res.body)

    def test_login_on_signup(self):
        res = self._register_user('robert', 'robert')
        res = res.follow()
        self.assertIn('Logout', res.body)
        self.assertIn('robert', res.body)

    def test_change_password(self):
        oldpass = 'alphonse'
        newpass = 'karr'
        res = self._register_user('alphonse', oldpass)
        res = res.follow()
        res = self.testapp.get('/profile')
        form = res.form
        form['oldpass'] = oldpass
        form['newpass'] = newpass
        res = form.submit('save')
        res = self._logout().follow()
        self.assertIn('Login', res.text)
        res = self.testapp.get('/login')
        res = self._login_helper('alphonse', newpass, res)
        res = res.follow()
        self.assertIn('Logout', res.text)

    def test_signal_route(self):
        res = self._register_user('tintin', 'milou')
        res = res.follow()
        #res = self.testapp.post('/signal', {'source': 'home',
            #'action': 'linkup', 'item': '1'}, status=200) TODO

    def test_admin_deny_anonymous(self):
        """
        Admin panel is denied to anonymous users
        """
        url = '/admin'
        res = self.testapp.get(url)
        self.assertIn('Password', res.body)

    def test_admin_deny_logged_in(self):
        """
        Admin panel is denied to ordinary citizens
        """
        username = 'alfred'
        password = 'alfredo'
        self._register_user(username, password)
        res = self.testapp.get('/login')
        res = self._login_helper(username, password, res)
        url = '/admin'
        res = self.testapp.get(url)
        self.assertIn('Password', res.body)

    def test_admin_allow(self):
        """
        Admin panel is granted to admin user
        """
        username = 'admin'
        password = 'admino'
        self._register_user(username, password)
        res = self.testapp.get('/login')
        res = self._login_helper(username, password, res)
        url = '/admin'
        res = self.testapp.get(url)
        self.assertNotIn('Password', res.body)
