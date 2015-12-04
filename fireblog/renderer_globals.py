from pyramid.events import BeforeRender
import fireblog.utils as utils
from fireblog.settings import settings_dict
from fireblog.models import (
    DBSession,
    Users
)
import logging


log = logging.getLogger(__name__)


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
        log.info('Did not get username for email {}'.format(email_address))
        return ''
    return user.username


def add_renderer_globals(event):
    event['settings_dict'] = settings_dict
    event['urlify'] = utils.urlify
    event['get_username'] = get_username


def includeme(config):
    config.add_request_method(get_bower_url)
    config.add_subscriber(add_renderer_globals, BeforeRender)
