import unittest
import transaction

from pyramid import testing
from pyramid.httpexceptions import HTTPFound

from .models import (
        DBSession,
        Base,
        MyModel,
        User,
        )

from .views import LoginView

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
            alfred = User("alfred", "alfredo")
            DBSession.add(alfred)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_home(self):
        from .views import view_home
        request = testing.DummyRequest()
        home = view_home(request)
        self.assertIn('Welcome', home['content'])

    def test_login_fail(self):
        user = dict(username="doesnotexist",
                    password="doesnotexist",
                    login="submit",
                    )
        request = testing.DummyRequest(user)
        lv = LoginView(request)()
        self.assertNotIsInstance(lv, HTTPFound)

    def test_login_ok(self):
        user = dict(username="alfred",
                    password="alfredo",
                    login="submit",
                    )
        request = testing.DummyRequest(user)
        lv = LoginView(request)()
        self.assertIsInstance(lv, HTTPFound)
