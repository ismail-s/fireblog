from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.security import Allow, ALL_PERMISSIONS
from sqlalchemy.orm.exc import NoResultFound
from fireblog.dogpile_region import region
from fireblog.models import (
    DBSession,
    Users
)
import logging


log = logging.getLogger(__name__)


class Root(object):
    """Resource tree to map groups to permissions. We allow admins to do
    anything, and commenters to be able to comment only.
    """
    __acl__ = [
        (Allow, 'g:admin', ALL_PERMISSIONS),
        (Allow, 'g:commenter', 'add-comment'),
    ]

    def __init__(self, request):
        self.request = request


@region.cache_on_arguments()
def groupfinder(userid):
    """Looks up and returns the groups the userid belongs to.
    If the userid doesn't exist, they are created as a commenter, and the
    group they belong to (g:commenter) is returned."""
    query = DBSession.query(Users.group). \
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
    log.info('New commenter {} has been created'.format(userid))
    return group


def includeme(config):
    settings = config.registry.settings
    config.include("pyramid_persona")
    config.commit()
    config.set_root_factory(Root)
    authn_policy = AuthTktAuthenticationPolicy(
        settings['persona.secret'],
        callback=lambda x, _: groupfinder(x))
    config.set_authentication_policy(authn_policy)
    # Pyramid_persona has already set an authorization policy, so
    # this has not been done here.
