from fireblog.compat import Path
from git import Repo
from alembic.script import ScriptDirectory
from alembic.config import Config
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from fireblog.theme import use_template, TemplateResponseDict
import re

current_dir = Path(__file__).parent
repo_dir = current_dir / '..'
repo = Repo(str(repo_dir))
git = repo.git


def an_update_is_available():
    '''returns 1 param: a bool for whether an update is available. No checks
    are made for whether the db also needs to be upgraded.'''
    # The method used here is detailed in http://stackoverflow.com/a/3278427.
    # Get updates from remotes
    repo.remotes.origin.update()
    # Get local, remote and base commit shas
    local = git.rev_parse('@')
    remote = git.rev_parse('@{u}')
    base = git.merge_base('@', '@{u}')
    if local == remote:
        return False
    if local == base:
        return True
    else:
        # Either more commits have been added here, or repos have diverged.
        # In either case, we don't want to be pulling in any changes.
        return False


def db_upgrade_is_required():
    '''Should only be called to see if the latest update will require a db
    upgrade. This function assumes that updates have already been fetched
    from the remote.
    This function uses exec on alembic migration files, but we are already
    trusting the code for the blog to be safe to run, so this is ok.'''
    # One way of doing this is to checkout the latest code, then run alembic to
    # check if we are current, and then revert the checkout... Technically,
    # this would work as we will be running code from memory. However, what if
    # the server lost power midway through? Then we would be in a pickle. So a
    # safer option is to analyse the git object db, see whether new alembic
    # files have been created, and if any of the new files reference the
    # current alembic version of the db. If so, then we know that we will need
    # to upgrade the db.

    # Get alembic versions in update
    alembic_heads = _get_current_alembic_revisions()
    if len(alembic_heads) > 1:
        # We have had a branch divergence, we should tell the user...
        return False  # TODO-change this...
    alembic_current = alembic_heads[0]
    update_sha = git.rev_parse('@{u}')
    update_migrations = repo.commit(update_sha).tree / 'alembic' / 'versions'
    update_filenames = set([blob.name for blob in update_migrations.blobs])
    # Get alembic versions in current working tree
    curr_migrations = (repo_dir / 'alembic' / 'versions').iterdir()
    existing_filenames = set(x.name for x in curr_migrations if x.is_file())
    new_files = update_filenames - existing_filenames
    if new_files:
        # Check the files to see if any of them are upgrades to the db
        for file in new_files:
            file_contents = update_migrations[file].data_stream.read()
            _globals, _locals = {}, {}
            try:
                exec(file_contents, _globals, _locals)
                if _locals['down_revision'] == alembic_current:
                    return True
            except:
                # If we can't exec the file, we just search it using a regex
                res = re.search(
                    'down_revision\s*=\s*(?P<rev>(?:None)|\w+)$',
                    file_contents)
                if res and eval(res.group('rev')) == alembic_current:
                    return True
    return False


def _get_current_alembic_revisions():
    config = Config(str(repo_dir / 'alembic.ini'))
    script = ScriptDirectory.from_config(config)
    return script.get_heads()


def update_to_latest_version():
    'Checkout the latest version of the code'
    git.pull()


@view_config(route_name='update_check', permission='update-blog',
             decorator=use_template('updater.mako'), request_method="GET")
def check_for_updates(request):
    update_available, db_upgrade_required = False, False
    if an_update_is_available():
        if db_upgrade_is_required():
            update_available, db_upgrade_required = True, True
        else:
            update_available, db_upgrade_required = True, False
    return TemplateResponseDict(update_available=update_available,
                                db_upgrade_required=db_upgrade_required,
                                save_url=request.route_url('update_check'))


@view_config(route_name='update_check', request_method="POST",
             request_param='form.submitted', permission='update-blog')
def update_blog(request):
    update_to_latest_version()
    return HTTPFound(location=request.route_url('reload_fireblog'))
