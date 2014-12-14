import transaction
import pytest
from sqlalchemy import create_engine
import datetime, copy

from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from myblog.models import DBSession, Base, Post, Users
import myblog.views as views
from myblog import add_routes

@pytest.fixture
def pyramid_req():
    return testing.DummyRequest()

@pytest.fixture
def mydb(request, scope='module'):
    engine = create_engine('sqlite://')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        post = Post(name='Homepage',
                    markdown='This is the front page',
                    html = '<p>This is the front page</p>',
                    created = datetime.datetime(2013, 1, 1))
        DBSession.add(post)
        post2 = Post(name='Page2',
                    markdown='This is page 2',
                    html = '<p>This is page 2</p>',
                    created = datetime.datetime(2014, 1, 1))
        DBSession.add(post2)
    with transaction.manager:
        me = Users(userid = 'id5489746@mockmyid.com',
                    group = 'g:admin')
        DBSession.add(me)
    def fin():
        DBSession.remove()
    request.addfinalizer(fin)
    return DBSession


@pytest.fixture
def pyramid_config(mydb, request):
    config = testing.setUp()
    add_routes(config)
    mydb.begin(subtransactions = True)
    def fin():
        testing.tearDown()
        mydb.rollback()
    request.addfinalizer(fin)
    return config


class Test_home:
    def test_success(self, pyramid_config, pyramid_req):
        response = views.home(pyramid_req)
        assert 'Page2' in response['title']
        assert response['prev_page'] == 'http://example.com/Homepage'
        assert response['next_page'] == None
        assert response['html'] == '<p>This is page 2</p>'


class Test_add_post:
    def test_GET_success(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'somenewpage'
        response = views.add_post(pyramid_req)
        assert 'somenewpage' in response['title']
        assert response['post_text'] == ''
        assert response['save_url'] == 'http://example.com/somenewpage/add'

    def test_GET_failure(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'Homepage'
        response = views.add_post(pyramid_req)
        assert response.location == 'http://example.com/Homepage/edit'

    def test_POST_success(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'somenewpage'
        pyramid_req.params['form.submitted'] = True
        pyramid_req.params['body'] = 'Some test body.'
        response = views.add_post(pyramid_req)
        assert response.location == 'http://example.com/somenewpage'

        del pyramid_req.params['body']
        del pyramid_req.params['form.submitted']
        response = views.view_post(pyramid_req)
        assert response['title'] == 'somenewpage'
        assert response['prev_page'] == 'http://example.com/Page2'
        assert response['next_page'] == None
        assert response['html'] == '<p>Some test body.</p>'


class Test_view_post:
    def test_success(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'Homepage'
        response = views.view_post(pyramid_req)
        assert response['title'] == 'Homepage'
        assert response['prev_page'] == None
        assert response['next_page'] == 'http://example.com/Page2'
        assert response['html'] == '<p>This is the front page</p>'

    def test_failure(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'nonexisting page'
        response = views.view_post(pyramid_req)
        assert type(response) == HTTPNotFound


class Test_edit_post:
    def test_GET_success(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'Homepage'
        response = views.edit_post(pyramid_req)
        assert 'Homepage' in response['title']
        assert response['post_text'] == 'This is the front page'
        assert response['save_url'] == 'http://example.com/Homepage/edit'

    def test_GET_failure(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'nonexisting page'
        response = views.edit_post(pyramid_req)
        assert response.location == 'http://example.com/'

    def test_POST_success(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'Homepage'
        pyramid_req.params['form.submitted'] = True
        pyramid_req.params['body'] = 'Some test body.'
        response = views.edit_post(pyramid_req)
        assert response.location == 'http://example.com/Homepage'

        del pyramid_req.params['body']
        del pyramid_req.params['form.submitted']
        response = views.view_post(pyramid_req)
        assert response['title'] == 'Homepage'
        assert response['prev_page'] == None
        assert response['next_page'] == 'http://example.com/Page2'
        assert response['html'] == '<p>Some test body.</p>'


class Test_del_post:
    def test_GET_success(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'Homepage'
        response = views.del_post(pyramid_req)
        assert 'Homepage' in response['title']
        assert response['save_url'] == 'http://example.com/Homepage/del'

    def test_GET_failure(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'nonexisting page'
        response = views.del_post(pyramid_req)
        assert response.location == 'http://example.com/'

    def test_POST_success(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'Homepage'
        pyramid_req.params['form.submitted'] = True
        response = views.del_post(pyramid_req)
        assert response.location == 'http://example.com/'

        del pyramid_req.params['form.submitted']
        response = views.view_post(pyramid_req)
        assert type(response) == HTTPNotFound
