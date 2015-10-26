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


def template_response_adapter(s: utils.TemplateResponseDict):
    """This function works in tandem with
    :py:class:`fireblog.utils.TemplateResponseDict`. This function assumes s
    is an instance of :py:func:`fireblog.utils.TemplateResponseDict` and
    returns a :py:class:`pyramid.response.Response` containing a string
    representation of s."""
    assert isinstance(s, utils.TemplateResponseDict)
    response = Response(repr(s))
    return response


def get_bower_url(request, path_to_resource: str) -> str:
    """Generate a url which points to the supplied path_or_resource.
    The path_or_resource must exist in the /bower_components folder which is
    located ../../bower_components relative to the file this function is in."""
    asset = 'fireblog:../bower_components/' + path_to_resource
    return request.static_url(asset)


def get_username(email_address: str):
    """Gets the username associated with the supplied email address from the
    db."""
    user = DBSession.query(Users.userid, Users.username).filter_by(
        userid=email_address).first()
    if not user:
        return ''
    return user.username


def add_username_function(event):
    event['get_username'] = get_username


def add_urlify_function(event):
    event['urlify'] = utils.urlify


def groupfinder(userid, request) -> list:
    """Looks up and returns the groups the userid belongs to.
    If the userid doesn't exist, they are created as a commenter, and the
    group they belong to (g:commenter) is returned."""
    query = DBSession.query(Users). \
        filter(Users.userid == userid)
    try:
        user = query.one()
        return [user.group]
    except NoResultFound:
        group = create_commenter_and_return_group(userid)
        return [group]


def create_commenter_and_return_group(userid) -> str:
    """This function assumes userid doesn't exist in the db, and creates a new
    user with this userid, as a commenter.

    :return: group the user belongs to (g:commenter)"""
    group = 'g:commenter'
    new_user = Users(userid=userid, group=group)
    DBSession.add(new_user)
    return group


class Root(object):
    """Rresource tree to map groups to permissions. We allow admins to do
    anything, and commenters to be able to comment only.
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
    config.include('fireblog.views')


def get_secret_settings(secrets_file: str, *, defaults: dict=None):
    """Open secrets_file, which should be a filepath to an ini file, read in
    the DEFAULT section of the ini file, and return this as a dict.

    :param defaults: A dict of defaults to pass to
        :py:class:`configparser.ConfigParser`.
    :return: dict
    """
    if not secrets_file:
        return {}
    secrets = ConfigParser(defaults=defaults)
    secrets.read(secrets_file)
    return dict(secrets['DEFAULT'])


def main(global_config, **settings):
    """This is the main function that runs the whole blog. It should in
    general not be called directly. Rather, run the command:

    .. code:: bash

        pserve development.ini

    Or use Python Paste's
    `loadapp <http://pythonpaste.org/deploy/#basic-usage>`_ function.

    :return: WSGI app
    """
    # Get extra config settings from secrets file
    secrets_file = settings.get('secrets', None)
    secrets_dict = get_secret_settings(secrets_file, defaults=global_config)
    settings.update(secrets_dict)

    allViewPostLen = int(settings.get('fireblog.all_view_post_len', 1000))
    settings['fireblog.all_view_post_len'] = allViewPostLen
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
