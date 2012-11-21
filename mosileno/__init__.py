from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from .models import (
    DBSession,
    Base,
)

from random import choice
from string import ascii_uppercase, digits


def generate_key(n):
    return ''.join(choice(ascii_uppercase + digits) for x in range(n))


def get_secret_key():
    filename = 'secret.key'
    try:
        with open(filename) as f:
            secret = f.read()
    except IOError as e:
        secret = generate_key(64)
        with open(filename, 'w+') as f:
            f.write(secret)
    return secret


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings,
                          root_factory='mosileno.models.RootFactory')
    secret_key = get_secret_key()
    authn = AuthTktAuthenticationPolicy(secret_key)
    authz = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn)
    config.set_authorization_policy(authz)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('expandedview', '/expandedview')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('signup', '/signup')
    config.add_route('feedadd', '/feed/add')
    config.add_route('feedview', '/feed/{slug}')
    config.add_route('profile', '/profile')
    config.add_route('feedview', '/feed/{feedid}')
    config.add_route('linkclick', '/linkclick')
    config.add_route('linkup', '/linkup')
    config.add_route('linkdown', '/linkdown')
    config.scan()
    return config.make_wsgi_app()
