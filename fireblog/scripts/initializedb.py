"""
The initializedb or initialize_fireblog_db script works in 2 ways:

1) It can initialise a db to be used for the blog
2) If a db already exists, then it will:

  a) Run migrations on it if necessary
  b) Check the settings table in the db and make sure that all required
     settings exist and are valid.
"""
import os
from fireblog.compat import Path
import sys
import transaction

from sqlalchemy import engine_from_config
from markdown import markdown
from pyramid.paster import (
    get_appsettings,
    setup_logging,
)
from alembic.config import Config
from alembic import command
from pyramid.scripts.common import parse_vars

from fireblog.models import (
    DBSession,
    Post,
    Users,
    Base,
)


first_post = """
If you can see this webpage correctly, then you've setup the blog
and got it working. Good on you!

When you ran the {script_name} script, you were asked to provide an admin
email address. Click the sign-in button on this page to sign in using that
email address. Note that, by default, this blog only allows you to login to
the blog as long as the blog is running on localhost:8080. This generally means
that you first login can *only* be done from the computer the blog is running
on. Once you have logged in with your admin account, then you can change the
settings to make logging in work for whatever domain you want to run the blog
on.

Once signed in, you can edit this post (posts are written in
[Markdown](http://daringfireball.net/projects/markdown/), add a new post,
delete posts and manage tags. I plan to add more functionality in the coming
months. As and when I get time.

For more information about this blog, see the
[github page](https://www.github.com/ismail-s/fireblog).
Any issues, report them there.
"""


def setup_first_post(DBSession, script_name):
    # Don't setup first post if posts already exist. This may be the case
    # if the script is run on an existing db.
    if DBSession.query(Post).count() > 0:
        print('Skipping setting up an initial post as there already exist '
              'posts in the db')
        return
    post_markdown = first_post.format(script_name=script_name)
    email_address = input('Please provide an admin email address: ')
    print('Creating the database for you...')
    with transaction.manager:
        post = Post(name='Hello World!',
                    markdown=post_markdown,
                    html=markdown(post_markdown))
        DBSession.add(post)
    with transaction.manager:
        me = Users(userid=email_address,
                   group='g:admin')
        DBSession.add(me)


def setup_settings_db():
    from fireblog.settings import make_sure_all_settings_exist_and_are_valid
    make_sure_all_settings_exist_and_are_valid()


def run_alembic_migrations():
    current_dir = Path(__file__).parent
    alembic_cfg_file = current_dir / '..' / '..' / 'alembic.ini'
    alembic_cfg = Config(str(alembic_cfg_file.resolve()))
    command.upgrade(alembic_cfg, "head")


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    run_alembic_migrations()
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    setup_first_post(DBSession, script_name=os.path.basename(argv[0]))
    setup_settings_db()
    print('The database has now been setup.')
    print('Run "uwsgi --ini-paste-logged {ini_file}" to start the blog'.format(
        ini_file=config_uri))
