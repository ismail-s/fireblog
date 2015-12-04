from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.response import Response
import fireblog.utils as utils
from fireblog.settings import (
    settings_dict,
    make_sure_all_settings_exist_and_are_valid
)
from fireblog.models import (
    DBSession,
    Base,
)
from configparser import ConfigParser
import logging


log = logging.getLogger(__name__)


def template_response_adapter(s: utils.TemplateResponseDict):
    """This function works in tandem with
    :py:class:`fireblog.utils.TemplateResponseDict`. This function assumes s
    is an instance of :py:func:`fireblog.utils.TemplateResponseDict` and
    returns a :py:class:`pyramid.response.Response` containing a string
    representation of s."""
    assert isinstance(s, utils.TemplateResponseDict)
    # We need to return a Response() object, as per the Pyramid specs. But we
    # want to not store a string in the Response yet, but an arbitrary dict
    # as after this function returns, :py:func:`use_template` will do further
    # processing on this arbitrary dict. So we set a custom field on this
    # Respnse object, which we can retrieve in :py:func:`use_template`.
    response = Response()
    response._fireblog_custom_response = s
    return response


def add_routes(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('uuid', '/uuid/{uuid}')
    config.add_route('rss', '/rss')
    config.add_route('view_all_posts', '/all_posts')
    config.add_route('reload_fireblog', '/reload')

    config.add_route('add_post', '/add_post/{postname}')
    config.add_route('view_post', '/posts/{id}/{postname}')
    config.add_route('change_post', '/posts/{id}/{postname}/{action}')

    config.add_route('tag_view', '/tags/{tag_name}')
    config.add_route('tag_manager', '/tags')


def include_all_components(config):
    add_routes(config)
    config.include('fireblog.renderer_globals')
    config.include('fireblog.settings')
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
    log.debug('Found secrets file {}'.format(secrets_file))
    secrets_dict = get_secret_settings(secrets_file, defaults=global_config)
    settings.update(secrets_dict)

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    make_sure_all_settings_exist_and_are_valid()
    # Add all settings from db that are needed for plugins (eg pyramid_persona)
    # so that the plugins can access these settings.
    for name, value in settings_dict.items():
        if not name.startswith('fireblog'):
            settings[name] = value

    config = Configurator(settings=settings)
    config.include('pyramid_mako')
    config.include('fireblog.login')
    config.add_static_view(name='bower', path='fireblog:../bower_components')
    config.add_response_adapter(
        template_response_adapter, utils.TemplateResponseDict)
    include_all_components(config)
    config.scan()
    return config.make_wsgi_app()
