import transaction
import pytest
from sqlalchemy import create_engine
import webtest
from webtest.app import AppError
import requests
import PyRSS2Gen
import datetime, copy, re

from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from myblog.models import DBSession, Base, Post, Users, Tags
import myblog.views as views
from myblog import add_routes, groupfinder
import myblog


data = requests.get('http://personatestuser.org/email_with_assertion/http%3A%2F%2Flocalhost').json()
email = data['email']
assertion = data['assertion']

@pytest.fixture
def pyramid_req():
    res = testing.DummyRequest()
    res.registry.settings.update({'myblog.allViewPostLen': 1000})
    return res

@pytest.fixture
def mydb(request, scope='module'):
    engine = create_engine('sqlite://')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        # TODO-add tags to this test data. Some tests may also need updating.
        tag1 = Tags(tag = 'tag1')
        tag2 = Tags(tag = 'tag2')
        DBSession.add(tag1)
        DBSession.add(tag2)
        post = Post(name='Homepage',
                    markdown='This is the front page',
                    html = '<p>This is the front page</p>',
                    created = datetime.datetime(2013, 1, 1))
        post.tags.append(tag1)
        DBSession.add(post)
        post2 = Post(name='Page2',
                    markdown='This is page 2',
                    html = '<p>This is page 2</p>',
                    created = datetime.datetime(2014, 1, 1))
        post2.tags.extend([tag1, tag2])
        DBSession.add(post2)
    with transaction.manager:
        me = Users(userid = 'id5489746@mockmyid.com',
                    group = 'g:admin')
        him = Users(userid = email,
                    group = 'g:admin')
        DBSession.add(me)
        DBSession.add(him)
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

@pytest.fixture
def testapp(mydb, scope = 'module'):
        settings =  {'sqlalchemy.url': 'sqlite://',
                    'persona.audiences': 'http://localhost',
                    'persona.secret': 'some_secret',
                    'myblog.allViewPostLen': 1000}
        app = myblog.main({}, **settings)
        testapp = webtest.TestApp(app)
        return testapp


class Test_home:
    def test_success(self, pyramid_config, pyramid_req):
        response = views.home(pyramid_req)
        assert 'Page2' in response['title']
        assert response['prev_page'] == 'http://example.com/posts/Homepage'
        assert response['next_page'] == None
        assert response['html'] == '<p>This is page 2</p>'


class Test_add_post:
    @staticmethod
    def submit_add_post(request, postname, body, tags):
        request.matchdict['postname'] = postname
        request.params['form.submitted'] = True
        request.params['body'] = body
        request.params['tags'] = tags
        res = views.add_post(request)
        del request.params['body']
        del request.params['form.submitted']
        del request.matchdict['postname']
        return res

    def test_GET_success(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'somenewpage'
        response = views.add_post(pyramid_req)
        assert 'somenewpage' in response['title']
        assert response['post_text'] == ''
        assert response['save_url'] == 'http://example.com/posts/somenewpage/add'

    def test_GET_failure(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'Homepage'
        response = views.add_post(pyramid_req)
        assert response.location == 'http://example.com/posts/Homepage/edit'

    def test_POST_success(self, pyramid_config, pyramid_req):
        postname = 'somenewpage'
        response = self.submit_add_post(pyramid_req, postname = postname,
                                        body = 'Some test body.',
                                        tags = 'tag2, tag1, tag2, ')
        assert response.location == 'http://example.com/posts/somenewpage'

        pyramid_req.matchdict['postname'] = postname
        response = views.view_post(pyramid_req)
        assert response['title'] == 'somenewpage'
        assert response['prev_page'] == 'http://example.com/posts/Page2'
        assert response['next_page'] == None
        assert response['html'] == '<p>Some test body.</p>'
        assert 'tag1' in response['tags']
        assert 'tag2' in response['tags']


class Test_view_post:
    def test_success(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'Homepage'
        response = views.view_post(pyramid_req)
        assert response['title'] == 'Homepage'
        assert response['prev_page'] == None
        assert response['next_page'] == 'http://example.com/posts/Page2'
        assert response['html'] == '<p>This is the front page</p>'

    def test_failure(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'nonexisting page'
        response = views.view_post(pyramid_req)
        assert type(response) == HTTPNotFound


class Test_view_all_posts:
    def test_success(self, pyramid_config, pyramid_req):
        response = views.view_all_posts(pyramid_req)
        assert response["code_styles"] == False
        posts = response["posts"]

        actual_posts = [("Page2", "<p>This is page 2</p>"),
                        ("Homepage", "<p>This is the front page</p>")]
        #post_names = [x[0] for x in actual_posts]

        for post, actual_post in zip(posts, actual_posts):
            assert post["name"] == actual_post[0]
            assert actual_post[1] in post["html"]
            # TODO-check that long posts are truncated correctly

    def test_success_with_pygments_code_css_included(self,
                                                    pyramid_config,
                                                    pyramid_req):
        post_name = 'tdghdht'
        post_body = '''some test body

```
#!python
def test(dfgv):
    pass
```

that is all.'''
        submit_res = Test_add_post.submit_add_post(pyramid_req,
                                            postname = post_name,
                                            body = post_body,tags='')

        # For some reason, we have to actually view the post before it appears
        # on view_all_posts page. Not sure why, but I'm not losing sleep over
        # this atm...
        pyramid_req.matchdict['postname'] = post_name
        view_res = views.view_post(pyramid_req)
        del pyramid_req.matchdict['postname']
        response = views.view_all_posts(pyramid_req)
        assert response["code_styles"] == True


class Test_edit_post:
    def test_GET_success(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'Homepage'
        response = views.edit_post(pyramid_req)
        assert 'Homepage' in response['title']
        assert response['post_text'] == 'This is the front page'
        assert response['save_url'] == 'http://example.com/posts/Homepage/edit'

    def test_GET_failure(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'nonexisting page'
        response = views.edit_post(pyramid_req)
        assert response.location == 'http://example.com/'

    def test_POST_success(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'Homepage'
        pyramid_req.params['form.submitted'] = True
        pyramid_req.params['body'] = 'Some test body.'
        pyramid_req.params['tags'] = 'test2, test1, test1'
        response = views.edit_post(pyramid_req)
        assert response.location == 'http://example.com/posts/Homepage'

        del pyramid_req.params['body']
        del pyramid_req.params['form.submitted']
        response = views.view_post(pyramid_req)
        assert response['title'] == 'Homepage'
        assert response['prev_page'] == None
        assert response['next_page'] == 'http://example.com/posts/Page2'
        assert response['html'] == '<p>Some test body.</p>'
        assert 'test1' in response['tags']
        assert 'test2' in response['tags']


class Test_del_post:
    def test_GET_success(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'Homepage'
        response = views.del_post(pyramid_req)
        assert 'Homepage' in response['title']
        assert response['save_url'] == 'http://example.com/posts/Homepage/del'

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


class Test_rss:
    # Basically, the lastBuildDate depends on when the render_rss_feed
    # function is called. So, I've separated the output into 2 strings,
    # omitting the lastBuildDate datetime. So everything else except
    # that is checked.
    rss_success_text_1 = '<?xml version="1.0" encoding="iso-8859-1"?>\n<rss version="2.0"><channel><title'
    '>Not the Answer</title><link>https://blog.ismail-s.com</link><description>A pers'
    'onal blog about science, computers and life.</description><lastBuildDate>'
    rss_success_text_2 = '</lastBuildDate><generator>PyRSS2Gen-1.1.0</generator><doc'
    's>http://blogs.law.harvard.edu/tech/rss</docs><item><title>Page2</title><link>ht'
    'tp://example.com/posts/Page2</link><description>&lt;p&gt;This is page 2&lt;/p&gt;</des'
    'cription><category>tag2</category><category>tag1</category><pubDate>Wed, 01 Jan 2014 00:00:00 GMT</pubDate></item><item><title>Hom'
    'epage</title><link>http://example.com/posts/Homepage</link><description>&lt;p&gt;This'
    ' is the front page&lt;/p&gt;</description><category>tag1</category><pubDate>Tue, 01 Jan 2013 00:00:00 GMT<'
    '/pubDate></item></channel></rss>'
    def test_success(self, pyramid_config, pyramid_req):
        response = views.render_rss_feed(pyramid_req)
        assert self.rss_success_text_1 in response.text
        assert self.rss_success_text_2 in response.text


class Test_tag_view:
    @pytest.mark.parametrize("tag, actual_posts", [
        ('tag1', [("Homepage", "<p>This is the front page</p>"),
                 ("Page2", "<p>This is page 2</p>")]),
        ('tag2', [("Page2", "<p>This is page 2</p>")])])
    def test_success(self, tag, actual_posts, pyramid_config, pyramid_req):
        pyramid_req.matchdict['tag_name'] = tag
        response = views.tag_view(pyramid_req)
        posts = response['posts']

        assert tag in response['title']
        assert not response['code_styles']

        for post, actual_post in zip(posts, actual_posts):
            assert post["name"] == actual_post[0]
            assert actual_post[1] in post["html"]
            # TODO-check that long posts are truncated correctly

    def test_failure(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['tag_name'] = 'doesntexist'
        response = views.tag_view(pyramid_req)
        assert type(response) == HTTPNotFound


class Test_groupfinder:
    @pytest.mark.parametrize('email_address',[
        'id5489746@mockmyid.com',
        email])
    def test_success(self, email_address, pyramid_config, pyramid_req):
        res = groupfinder(email_address, pyramid_req)
        assert res == ['g:admin']

    def test_failure(self, pyramid_config, pyramid_req):
        res = groupfinder('some_fake_address@example.com', pyramid_req)
        assert res == None


class Test_functional_tests:
    def get_csrf_token(self, testapp):
        res = testapp.get('http://localhost/')
        return re.search(r"csrf_token: '(?P<token>[a-zA-Z0-9]+)'",
                            str(res.html)).group('token')

    def login(self, testapp):
        csrf_token = self.get_csrf_token(testapp)
        viewer_login = '/login?csrf_token={}'.format(csrf_token)
        return testapp.post(viewer_login, dict(assertion=assertion,
                                                came_from = '/'))

    def logout(self, testapp):
        csrf_token = self.get_csrf_token(testapp)
        return testapp.post('/logout?csrf_token={}'.format(csrf_token),
                            dict(came_from = '/'))

    def test_homepage(self, testapp):
        res = testapp.get('http://localhost/')
        assert res.status == '200 OK'
        assert '<h1>Page2</h1>' in str(res.html)
        assert '<p>This is page 2</p>' in str(res.html)

    def test_get_page(self, testapp):
        res = testapp.get('http://localhost/posts/Page2')
        assert res.status == '200 OK'
        assert '<h1>Page2</h1>' in str(res.html)
        assert '<p>This is page 2</p>' in str(res.html)

    def test_login(self, testapp):
        res = self.login(testapp)
        assert res.status == '200 OK'

        correct_res = {'success': True, 'redirect': '/'}
        assert res.json == correct_res
        self.logout(testapp)

    def test_logout(self, testapp):
        res = self.logout(testapp)
        assert res.status == '200 OK'
        assert res.json == {'redirect': '/'}

    def test_can_access_edit_pages_after_logging_in(self, testapp):
        self.login(testapp)
        res = testapp.get('/posts/Page2/edit')
        assert res.status == '200 OK'
        assert 'This is page 2' in str(res.html)
        self.logout(testapp)

    def test_can_access_del_pages_after_logging_in(self, testapp):
        self.login(testapp)
        res = testapp.get('/posts/Page2/del')
        assert res.status == '200 OK'
        # TODO-add more checks over here maybe
        self.logout(testapp)

    def test_can_access_add_pages_after_logging_in(self, testapp):
        self.login(testapp)
        res = testapp.get('/posts/some new page/add')
        assert res.status == '200 OK'
        assert 'some new page' in str(res.html)
        self.logout(testapp)

    def test_cant_access_edit_pages_without_logging_in(self, testapp):
        with pytest.raises(AppError) as excinfo:
            res = testapp.get('/posts/Page2/edit')
        assert '403 Forbidden' in str(excinfo.value)

    def test_cant_access_del_pages_without_logging_in(self, testapp):
        with pytest.raises(AppError) as excinfo:
            res = testapp.get('/posts/Page2/del')
        assert '403 Forbidden' in str(excinfo.value)

    def test_cant_access_add_pages_without_logging_in(self, testapp):
        with pytest.raises(AppError) as excinfo:
            res = testapp.get('/posts/some random page/add')
        assert '403 Forbidden' in str(excinfo.value)

    def test_crud(self, testapp):
        """Testing all CRUD operations in one big test."""
        self.login(testapp)

        # 1. Create a post
        res = testapp.get('/posts/some new page/add')
        form = res.forms["edit-post"]
        form["body"] = 'This is a test body.'
        form["tags"] = 'test2, test1, test1'
        res = form.submit('form.submitted')

        # 2. Read the post
        res = testapp.get('/posts/some new page')
        assert res.status == '200 OK'
        assert '<h1>some new page</h1>' in str(res.html)
        assert '<p>This is a test body.</p>' in str(res.html)
        assert 'test1' in str(res.html)
        assert 'test2' in str(res.html)
        assert '/tags/test1' in str(res.html)
        assert '/tags/test2' in str(res.html)

        # 3. Edit the post
        res = res.click(href = r'.*/edit')
        form = res.forms["edit-post"]
        form["body"] = 'This is a brand new test body.'
        assert form["tags"].value == 'test1, test2'
        form["tags"] = 'test2, test3'
        res = form.submit('form.submitted')

        # 4. Test the post has been updated
        res = testapp.get('/posts/some new page')
        assert res.status == '200 OK'
        assert '<h1>some new page</h1>' in str(res.html)
        assert '<p>This is a brand new test body.</p>' in str(res.html)
        assert 'test2' in str(res.html)
        assert 'test3' in str(res.html)
        assert '/tags/test2' in str(res.html)
        assert '/tags/test3' in str(res.html)

        # 5. Delete the post
        res = res.click(href = r'.*/del')
        form = res.forms["del-post"]
        res = form.submit('form.submitted')

        # 6. Test we get a 404 on trying to read the post
        with pytest.raises(AppError) as excinfo:
            res = testapp.get('/posts/some new page')
        assert '404 Not Found' in str(excinfo.value)
