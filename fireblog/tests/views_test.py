import pytest
import re


from pyramid.httpexceptions import HTTPNotFound

import fireblog.views as views
from fireblog.views import Post_modifying_views, Add_Post


class Test_home:

    def test_success(self, pyramid_config, pyramid_req):
        response = views.home(pyramid_req)
        assert 'Page2' in response['title']
        prev_page_regex = (
            r'(?:http://(?:localhost|example\.com)'
            r'/posts/1/Homepage)\Z')
        assert re.match(prev_page_regex, response['prev_page'])
        assert response['next_page'] is None
        assert response['html'] == '<p>This is page 2</p>'


class Test_add_post:

    @staticmethod
    def submit_add_post(request, postname, body, tags):
        request.matchdict['postname'] = postname
        request.params['form.submitted'] = True
        request.params['body'] = body
        request.params['tags'] = tags
        res = Add_Post(request).add_post_POST()
        del request.params['body']
        del request.params['form.submitted']
        del request.matchdict['postname']
        return res

    def test_GET_success(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'somenewpage'
        response = Add_Post(pyramid_req).add_post()
        assert 'somenewpage' in response['title']
        assert response['post_text'] == ''
        assert response[
            'save_url'] == 'http://example.com/add_post/somenewpage'

    def test_GET_failure(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'Homepage'
        response = Add_Post(pyramid_req).add_post()
        assert response.location == 'http://example.com/posts/1/Homepage/edit'

    def test_POST_success(self, pyramid_config, pyramid_req):
        # Get Page2 post into dogpile_cache
        pyramid_req.matchdict['postname'] = 'Page2'
        pyramid_req.matchdict['id'] = 2
        views.view_post(pyramid_req)

        postname = 'somenewpage'
        response = self.submit_add_post(pyramid_req, postname=postname,
                                        body='Some test body.',
                                        tags='tag2, tag1, tag2, ')
        assert response.location == 'http://example.com/'

        pyramid_req.matchdict['postname'] = postname
        pyramid_req.matchdict['id'] = 3
        response = views.view_post(pyramid_req)
        assert response['title'] == 'somenewpage'
        assert response['prev_page'] == ('http://example.com/'
                                         'posts/2/Page2-1%2A2')
        assert response['next_page'] is None
        assert response['html'] == '<p>Some test body.</p>'
        assert 'tag1' in response['tags']
        assert 'tag2' in response['tags']

        # Check the previous post has a link to this one
        pyramid_req.matchdict['postname'] = 'Page2'
        pyramid_req.matchdict['id'] = 2
        response = views.view_post(pyramid_req)
        assert response[
            'next_page'] == 'http://example.com/posts/3/' + postname

    def test_POST_failure(self, pyramid_config, pyramid_req):
        response = self.submit_add_post(pyramid_req, postname='Homepage',
                                        body='Some test body.',
                                        tags='tag2')
        assert response.location == 'http://example.com/posts/1/Homepage/edit'


class Test_view_post:

    def test_success(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'Homepage'
        pyramid_req.matchdict['id'] = 1
        response = views.view_post(pyramid_req)
        assert response['title'] == 'Homepage'
        assert response['prev_page'] is None
        assert response['next_page'] == ('http://example.com/'
                                         'posts/2/Page2-1%2A2')
        assert response['html'] == '<p>This is the front page</p>'
        assert response['uuid'] == 'uuid-post-homepage'
        assert 'tag1' in response['tags']
        assert 'tag2' not in response['tags']
        assert response['post_date'] == '01 Jan 2013'

    def test_failure(self, pyramid_config, pyramid_req):
        # Check that we fail if the id isn't matched (regardless of the
        # postname)
        pyramid_req.matchdict['postname'] = 'Homepage'
        pyramid_req.matchdict['id'] = 3
        response = views.view_post(pyramid_req)
        assert isinstance(response, HTTPNotFound)


class Test_view_all_posts:

    def test_success(self, pyramid_config, pyramid_req):
        response = views.view_all_posts(pyramid_req)
        assert response["code_styles"] is False
        posts = response["posts"]

        actual_posts = [("Page2 1*2", "<p>This is page 2</p>"),
                        ("Homepage", "<p>This is the front page</p>")]

        for post, actual_post in zip(posts, actual_posts):
            assert post["name"] == actual_post[0]
            assert actual_post[1] in post["html"]

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
        Test_add_post.submit_add_post(pyramid_req,
                                      postname=post_name,
                                      body=post_body, tags='')

        # For some reason, we have to actually view the post before it appears
        # on view_all_posts page. Not sure why, but I'm not losing sleep over
        # this atm...
        pyramid_req.matchdict['postname'] = post_name
        pyramid_req.matchdict['id'] = 3
        views.view_post(pyramid_req)
        del pyramid_req.matchdict['postname']
        response = views.view_all_posts(pyramid_req)
        assert response["code_styles"]

    @pytest.mark.parametrize('body, html', [('S' * 998 + 'a', "<p>" + "S" * 998 + 'a' + "</p>"), ('S' * 999 + 'a', "<p>" + "S" * 999 + 'a' + "</p>"),
                            ('S' * 1000 + 'a', "<p>" + "S" * 1000 + '...' + "</p>")])
    def test_long_posts_get_truncated(self, body, html, mydb, pyramid_config, pyramid_req):
        # Make the Homepage post really long
        pyramid_req.matchdict = {'postname': 'Homepage', 'id': 1}
        pyramid_req.params = {'form.submitted': True, 'tags': ''}
        pyramid_req.params['body'] = body
        Post_modifying_views(pyramid_req).edit_post_POST()
        # Get rid of the only other post
        pyramid_req.matchdict = {'postname': 'Page2', 'id': 2}
        pyramid_req.params['form.submitted'] = True
        response = Post_modifying_views(pyramid_req).del_post_POST()
        mydb.flush()
        pyramid_req.matchdict = {}
        pyramid_req.params = {}
        response = views.view_all_posts(pyramid_req)
        posts = response["posts"]

        expected_res =  {"name": "Homepage", "html": html}

        for e, v in expected_res.items():
            assert posts[0][e] == v
        # for post, actual_post in zip(posts, actual_posts):
        #     assert post["name"] == actual_post[0]
        #     assert actual_post[1] in post["html"]


class Test_edit_post:

    def test_GET_success(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'Homepage'
        pyramid_req.matchdict['id'] = 1
        response = Post_modifying_views(pyramid_req).edit_post()
        assert 'Homepage' in response['title']
        assert response['post_text'] == 'This is the front page'
        assert response['save_url'] == ('http://example.com/'
                                        'posts/1/Homepage/edit')

    def test_GET_failure(self, pyramid_config, pyramid_req):
        # Only the id should be being checked, not the postname
        pyramid_req.matchdict['postname'] = 'Homepage'
        pyramid_req.matchdict['id'] = 3
        response = Post_modifying_views(pyramid_req).edit_post()
        assert response.location == 'http://example.com/'

    def test_POST_success(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'Homepage'
        pyramid_req.matchdict['id'] = 1
        pyramid_req.params['form.submitted'] = True
        pyramid_req.params['body'] = 'Some test body.'
        pyramid_req.params['tags'] = 'test2, test1, test1'
        response = Post_modifying_views(pyramid_req).edit_post_POST()
        assert response.location == 'http://example.com/posts/1/Homepage'

        del pyramid_req.params['body']
        del pyramid_req.params['form.submitted']
        response = views.view_post(pyramid_req)
        assert response['title'] == 'Homepage'
        assert response['prev_page'] is None
        assert response['next_page'] == ('http://example.com/'
                                         'posts/2/Page2-1%2A2')
        assert response['html'] == '<p>Some test body.</p>'
        assert 'test1' in response['tags']
        assert 'test2' in response['tags']

    def test_POST_failure(self, pyramid_config, pyramid_req):
        # Only the id should be being checked, not the postname
        pyramid_req.matchdict['postname'] = 'Homepage'
        pyramid_req.matchdict['id'] = 3
        response = Post_modifying_views(pyramid_req).edit_post_POST()
        assert response.location == 'http://example.com/'


class Test_del_post:

    def test_GET_success(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'Homepage'
        pyramid_req.matchdict['id'] = 1
        response = Post_modifying_views(pyramid_req).del_post()
        assert 'Homepage' in response['title']
        assert response['save_url'] == ('http://example.com/'
                                        'posts/1/Homepage/del')

    def test_GET_failure(self, pyramid_config, pyramid_req):
        # Here, we use the same postname as an existing post, but use a
        # different id.
        pyramid_req.matchdict['postname'] = 'Homepage'
        pyramid_req.matchdict['id'] = 3
        response = Post_modifying_views(pyramid_req).del_post()
        assert response.location == 'http://example.com/'

    def test_POST_success(self, pyramid_config, pyramid_req):
        # 1. Get Homepage and somenewpost into dogpile_cache.
        pyramid_req.matchdict = {'postname': 'Homepage', 'id': 1}
        views.view_post(pyramid_req)
        pyramid_req.matchdict = {'postname': 'somenewpost', 'id': 3}
        views.view_post(pyramid_req)
        # 2. Add a new post, so we have 3 posts.
        Test_add_post.submit_add_post(
            pyramid_req,
            postname='somenewpost',
            body='Some test body.',
            tags='tag2, tag1, tag2')
        # 3. Delete the middle post
        pyramid_req.matchdict['postname'] = 'Page2'
        pyramid_req.matchdict['id'] = 2

        pyramid_req.params['form.submitted'] = True
        response = Post_modifying_views(pyramid_req).del_post_POST()
        assert response.location == 'http://example.com/'
        # 4. Check the post has been deleted
        del pyramid_req.params['form.submitted']
        response = views.view_post(pyramid_req)
        assert isinstance(response, HTTPNotFound)
        # 5. Check the newest post now links to the first post
        pyramid_req.matchdict['postname'] = 'somenewpost'
        pyramid_req.matchdict['id'] = 3
        response = views.view_post(pyramid_req)
        assert response['prev_page'] == 'http://example.com/posts/1/Homepage'
        # 6. Check the first post links to the newest post (ie the cache key
        # has been deleted)
        pyramid_req.matchdict['postname'] = 'Homepage'
        pyramid_req.matchdict['id'] = 1
        response = views.view_post(pyramid_req)
        assert response[
            'next_page'] == 'http://example.com/posts/3/somenewpost'

    def test_POST_failure(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['postname'] = 'Homepage'
        pyramid_req.matchdict['id'] = 3
        response = Post_modifying_views(pyramid_req).del_post_POST()
        assert response.location == 'http://example.com/'


class Test_rss:
    # Basically, the lastBuildDate depends on when the render_rss_feed
    # function is called. So, I've separated the output into 2 strings,
    # omitting the lastBuildDate datetime. So everything else except
    # that is checked.
    rss_success_text_1 = ''
    '<?xml version="1.0" encoding="iso-8859-1"?>\n<rss version="2.0"><channel>'
    '<title>Not the Answer</title><link>https://blog.ismail-s.com</link>'
    '<description>A personal blog about science, computers and life.'
    '</description><lastBuildDate>'
    rss_success_text_2 = ''
    '</lastBuildDate><generator>PyRSS2Gen-1.1.0</generator><docs>'
    'http://blogs.law.harvard.edu/tech/rss</docs><item><title>Page2</title>'
    '<link>http://example.com/posts/Page2</link><description>&lt;p&gt;'
    'This is page 2&lt;/p&gt;</description><category>tag2</category>'
    '<category>tag1</category><pubDate>Wed, 01 Jan 2014 00:00:00 GMT</pubDate>'
    '</item><item><title>Homepage</title><link>'
    'http://example.com/posts/Homepage</link><description>&lt;p&gt;This is '
    'the front page&lt;/p&gt;</description><category>tag1</category>'
    '<pubDate>Tue, 01 Jan 2013 00:00:00 GMT</pubDate></item></channel></rss>'

    def test_success(self, pyramid_config, pyramid_req):
        response = views.render_rss_feed(pyramid_req)
        assert self.rss_success_text_1 in response.text
        assert self.rss_success_text_2 in response.text


class Test_uuid:

    @pytest.mark.parametrize('uuid, location', [
        ('uuid-post-homepage', 'http://example.com/posts/1/Homepage'),
        ('uuid-post-page2', 'http://example.com/posts/2/Page2-1%2A2'),
        ('uuid-post-h', 'http://example.com/posts/1/Homepage'),
        ('uuid-post-p', 'http://example.com/posts/2/Page2-1%2A2')])
    def test_post_success(self, uuid, location, pyramid_config, pyramid_req):
        pyramid_req.matchdict['uuid'] = uuid
        response = views.uuid(pyramid_req)
        assert response.location == location

    @pytest.mark.parametrize('uuid, location', [
        ('uuid-tag111', 'http://example.com/tags/tag1'),
        ('uuid-tag222', 'http://example.com/tags/tag2'),
        ('uuid-tag1', 'http://example.com/tags/tag1'),
        ('uuid-tag2', 'http://example.com/tags/tag2')])
    def test_tag_success(self, uuid, location, pyramid_config, pyramid_req):
        pyramid_req.matchdict['uuid'] = uuid
        response = views.uuid(pyramid_req)
        assert response.location == location

    @pytest.mark.parametrize('uuid', ['uuid-post-', 'uuid-tag'])
    def test_multiple_results(self, uuid, pyramid_config, pyramid_req):
        pyramid_req.matchdict['uuid'] = uuid
        response = views.uuid(pyramid_req)
        assert not response.location

    @pytest.mark.parametrize('uuid', ['Uuid-post-', 'uuid-tagg'])
    def test_no_results(self, uuid, pyramid_config, pyramid_req):
        pyramid_req.matchdict['uuid'] = uuid
        response = views.uuid(pyramid_req)
        assert not response.location
