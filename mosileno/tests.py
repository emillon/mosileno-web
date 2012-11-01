import unittest
import transaction
import pyramid_celery

from mock import Mock

from StringIO import StringIO

from pyramid import testing
from pyramid.httpexceptions import HTTPFound

from .models import (
        DBSession,
        Base,
        MyModel,
        User,
        Feed,
        Subscription
        )

from .views import (
        LoginView,
        view_home,
        logout,
        SignupView,
        FeedAddView,
        OPMLImportView,
        )

class TestMyView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            model = MyModel(name='one', value=55)
            DBSession.add(model)
            alfred = User("alfred", "alfredo", workfactor=1)
            DBSession.add(alfred)
        self.config.testing_securitypolicy(userid='alfred', permissive=False)
        celery_settings = {'CELERY_ALWAYS_EAGER': True}
        config = Mock()
        config.registry = Mock()
        config.registry.settings = celery_settings
        pyramid_celery.includeme(config)

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
        find_feed = DBSession.query(Feed).filter(Feed.url==url)
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

class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from mosileno import main
        params = {'sqlalchemy.url': 'sqlite://'}
        app = main({}, **params)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertIn('Welcome', res.body)
