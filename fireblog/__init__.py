from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from fireblog.models import (
    DBSession,
    Base,
)
from configparser import ConfigParser
import logging


log = logging.getLogger(__name__)


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
    config.include('fireblog.theme')
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
    config = Configurator(settings=settings)
    # A lot of stuff, such as settings_dict, relies on the cache being setup,
    # so we set it up as soon as possible.
    config.include('pyramid_dogpile_cache')
    # Get extra config settings from secrets file
    secrets_file = settings.get('secrets', None)
    log.debug('Found secrets file {}'.format(secrets_file))
    secrets_dict = get_secret_settings(secrets_file, defaults=global_config)
    config.add_settings(secrets_dict)

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    # We have to import the settings module after setting up the cache, which
    # is done at the beginnning of this function.
    from fireblog.settings import (
        settings_dict,
        make_sure_all_settings_exist_and_are_valid
    )
    make_sure_all_settings_exist_and_are_valid()
    # Add all settings from db that are needed for plugins (eg pyramid_persona)
    # so that the plugins can access these settings.
    for name, value in settings_dict.items():
        if not name.startswith('fireblog'):
            config.add_settings({name: value})
    config.include('pyramid_tm')
    config.include('pyramid_persona')
    config.include('pyramid_mako')
    config.include('fireblog.login')
    config.add_static_view(name='bower', path='fireblog:../bower_components')
    include_all_components(config)
    config.scan()
    return config.make_wsgi_app()
