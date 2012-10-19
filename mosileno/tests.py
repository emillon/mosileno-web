import unittest
import transaction

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
        count_s = DBSession.query(Subscription).filter(Subscription.id==feed_id).count()
        self.assertEqual(count_s, 1)

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
