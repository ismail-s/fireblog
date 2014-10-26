from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy.orm.exc import NoResultFound
from pyramid.security import Allow, ALL_PERMISSIONS
from pyramid.authentication import AuthTktAuthenticationPolicy
from .models import (
    DBSession,
    Base,
    Users
    )

def groupfinder(userid, request):
    query = DBSession.query(Users).\
                filter(Users.userid == userid)
    try:
        user = query.one()
        return [user.group]
    except NoResultFound:
        return None

class Root(object):
    """Simplest possible resource tree to map groups to permissions.
    """
    __acl__ = [
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings, root_factory=Root)
    config.include('pyramid_mako')
    config.include("pyramid_persona")
    authn_policy = AuthTktAuthenticationPolicy(
    settings['persona.secret'],
    callback=groupfinder)
    config.set_authentication_policy(authn_policy)
    # Pyramid_persona has already set an authorization policy, so
    # this has not been done here.
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('view_post', '/{postname}')
    config.add_route('add_post', '/{postname}/add')
    config.add_route('edit_post', '/{postname}/edit')
    config.add_route('del_post', '/{postname}/del')
    config.scan()
    return config.make_wsgi_app()