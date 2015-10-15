from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy.orm.exc import NoResultFound
from pyramid.security import Allow, ALL_PERMISSIONS
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.events import BeforeRender
from pyramid.response import Response
import fireblog.utils as utils
from fireblog.models import (
    DBSession,
    Base,
    Users
)
from configparser import ConfigParser


def template_response_adapter(s):
    response = Response(repr(s))
    return response


def get_bower_url(request, path_to_resource):
    asset = 'fireblog:../bower_components/' + path_to_resource
    return request.static_url(asset)


def get_username(email_address):
    user = DBSession.query(Users.userid, Users.username).filter_by(
        userid=email_address).first()
    if not user:
        return ''
    return user.username


def add_username_function(event):
    event['get_username'] = get_username


def add_urlify_function(event):
    event['urlify'] = utils.urlify


def groupfinder(userid, request):
    query = DBSession.query(Users). \
        filter(Users.userid == userid)
    try:
        user = query.one()
        return [user.group]
    except NoResultFound:
        group = create_commenter_and_return_group(userid)
        return [group]


def create_commenter_and_return_group(userid):
    group = 'g:commenter'
    new_user = Users(userid=userid, group=group)
    DBSession.add(new_user)
    return group


class Root(object):
    """Simplest possible resource tree to map groups to permissions.
    """
    __acl__ = [
        (Allow, 'g:admin', ALL_PERMISSIONS),
        (Allow, 'g:commenter', 'add-comment'),
    ]

    def __init__(self, request):
        self.request = request


def add_routes(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('uuid', '/uuid/{uuid}')
    config.add_route('rss', '/rss')
    config.add_route('view_all_posts', '/all_posts')

    config.add_route('add_post', '/add_post/{postname}')
    config.add_route('view_post', '/posts/{id}/{postname}')
    config.add_route('change_post', '/posts/{id}/{postname}/{action}')

    config.add_route('tag_view', '/tags/{tag_name}')
    config.add_route('tag_manager', '/tags')

    config.add_subscriber(add_username_function, BeforeRender)
    config.add_subscriber(add_urlify_function, BeforeRender)


def include_all_components(config):
    add_routes(config)
    config.include('fireblog.comments', route_prefix='/comment')


def get_secret_settings(secrets_file, *, defaults=None):
    if not secrets_file:
        return {}
    secrets = ConfigParser(defaults=defaults)
    secrets.read(secrets_file)
    return dict(secrets['DEFAULT'])


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # Get extra config settings from secrets file
    secrets_file = settings.get('secrets', None)
    secrets_dict = get_secret_settings(secrets_file, defaults=global_config)
    settings.update(secrets_dict)

    allViewPostLen = int(settings.get('fireblog.allViewPostLen', 1000))
    settings['fireblog.allViewPostLen'] = allViewPostLen
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings, root_factory=Root)
    config.include('pyramid_mako')
    config.include("pyramid_persona")
    config.add_static_view(name='bower', path='fireblog:../bower_components')
    config.add_request_method(get_bower_url)
    config.add_response_adapter(
        template_response_adapter, utils.TemplateResponseDict)
    authn_policy = AuthTktAuthenticationPolicy(
        settings['persona.secret'],
        callback=groupfinder)
    config.set_authentication_policy(authn_policy)
    # Pyramid_persona has already set an authorization policy, so
    # this has not been done here.
    include_all_components(config)
    config.scan()
    return config.make_wsgi_app()
