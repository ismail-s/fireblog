import pytest
import transaction
import requests
import os
import datetime
import webtest
from pyramid import testing
from fireblog import include_all_components
from sqlalchemy import create_engine
from fireblog.models import (
    DBSession, Base, Post, Users, Tags, Comments, Settings
)
from fireblog.dogpile_region import region
import fireblog

# Get all available themes
theme_folder = os.path.join(os.path.dirname(__file__), '../templates')
available_themes = next(os.walk(theme_folder))[1]


def clear_dogpile_region():
    region.backend._cache = {}


@pytest.fixture(params=available_themes, scope='session')
def theme(request):
    return request.param


@pytest.fixture(scope='session')
def test_with_one_theme(theme):
    if theme != 'bootstrap':
        pytest.skip("This test doesn't need to be run against all themes.")


@pytest.fixture(scope='session')
def persona_test_admin_login():
    data = requests.get(
        'http://personatestuser.org/email_with_assertion/'
        'http%3A%2F%2Flocalhost')
    data = data.json()
    res = {}
    res['email'] = data['email']
    res['assertion'] = data['assertion']
    return res


@pytest.fixture
def pyramid_req():
    res = testing.DummyRequest()
    res.registry.settings.update({'dogpile_cache.backend': 'memory'})
    return res


@pytest.fixture
def mydb(request, persona_test_admin_login, theme):
    engine = create_engine('sqlite://')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        tag1 = Tags(tag='tag1', uuid='uuid-tag111')
        tag2 = Tags(tag='tag2', uuid='uuid-tag222')
        tag3 = Tags(tag='tag3', uuid='uuid-tag333')
        DBSession.add(tag1)
        DBSession.add(tag2)
        DBSession.add(tag3)
        post = Post(id=1,
                    name='Homepage',
                    markdown='This is the front page',
                    html='<p>This is the front page</p>',
                    created=datetime.datetime(2013, 1, 1),
                    uuid='uuid-post-homepage')
        post.tags.append(tag1)
        DBSession.add(post)
        post2 = Post(id=2,
                     name='Page2 1*2',  # Spaces and * test utils.urlify func.
                     markdown='This is page 2',
                     html='<p>This is page 2</p>',
                     created=datetime.datetime(2014, 1, 1),
                     uuid='uuid-post-page2')
        post2.tags.extend([tag1, tag2])
        DBSession.add(post2)
    with transaction.manager:
        me = Users(userid='id5489746@mockmyid.com',
                   group='g:admin')
        him = Users(userid=persona_test_admin_login['email'],
                    group='g:admin')
        commenter = Users(userid='commenter@example.com',
                          group='g:commenter')
        DBSession.add(me)
        DBSession.add(him)
        DBSession.add(commenter)
    with transaction.manager:
        comment1 = Comments(created=datetime.datetime(2014, 1, 1),
                            comment='test comment',
                            uuid='comment1-uuid')
        comment1.post = post
        comment1.author = me
        DBSession.add(comment1)
    with transaction.manager:
        settings_map = (
            ('fireblog.max_rss_items', '100'),
            ('fireblog.all_view_post_len', '1000'),
            ('persona.siteName', 'sitename'),
            ('persona.secret', 'seekret'),
            ('persona.audiences', 'http://localhost'),
            ('fireblog.recaptcha_secret',
             'secretsecretsecretsecretsecretsecretsecr'),
            ('fireblog.recaptcha_site_key',
             'secretsecretsecretsecretsecretsecretsecr'),
            ('fireblog.theme', theme))
        settings = [Settings(name=x, value=y) for x, y in settings_map]
        for e in settings:
            DBSession.add(e)

    def fin():
        DBSession.remove()
    request.addfinalizer(fin)
    return DBSession


@pytest.fixture
def pyramid_config(mydb, request):
    config = testing.setUp()
    config.include('pyramid_mako')
    include_all_components(config)
    mydb.rollback()
    mydb.begin(subtransactions=True)
    clear_dogpile_region()

    def fin():
        testing.tearDown()
        mydb.rollback()
        clear_dogpile_region()
    request.addfinalizer(fin)
    return config


@pytest.fixture
def setup_testapp(mydb, request):
    settings = {'sqlalchemy.url': 'sqlite://',
                'persona.audiences': 'http://localhost',
                'persona.secret': 'some_secret',
                'dogpile_cache.backend': 'memory',
                'fireblog.all_view_post_len': 1000,
                # max_rss_items is set as a str to test that
                # the rss view converts it to an int
                'fireblog.max_rss_items': '100',
                'fireblog.recaptcha_secret': 's' * 40,
                'fireblog.recaptcha_site_key': 's' * 40}
    mydb.rollback()
    app = fireblog.main({}, **settings)
    return webtest.TestApp(app)


@pytest.fixture
def testapp(request, mydb, setup_testapp):
    testapp = setup_testapp
    mydb.begin(subtransactions=True)
    clear_dogpile_region()

    def fin():
        mydb.rollback()
        clear_dogpile_region()
    request.addfinalizer(fin)
    return testapp
