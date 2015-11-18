import pytest
import fireblog.tags
from fireblog.views import Post_modifying_views
from pyramid.httpexceptions import HTTPNotFound


pytestmark = pytest.mark.usefixtures("test_with_one_theme")


class Test_tag_view:

    @pytest.mark.parametrize("tag, actual_posts", [
        ('tag1', [("Homepage", "<p>This is the front page</p>"),
                  ("Page2 1*2", "<p>This is page 2</p>")]),
        ('tag2', [("Page2 1*2", "<p>This is page 2</p>")])])
    def test_success(self, tag, actual_posts, pyramid_config, pyramid_req):
        pyramid_req.matchdict['tag_name'] = tag
        response = fireblog.tags.tag_view(pyramid_req)
        posts = response['posts']

        assert tag in response['title']
        assert not response['code_styles']

        for post, actual_post in zip(posts, actual_posts):
            assert post["name"] == actual_post[0]
            assert actual_post[1] in post["html"]

    def test_failure(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['tag_name'] = 'doesntexist'
        response = fireblog.tags.tag_view(pyramid_req)
        assert isinstance(response, HTTPNotFound)

    @pytest.mark.parametrize('body, html', [
        ('S' * 998 + 'a', "<p>" + "S" * 998 + 'a' + "</p>"),
        ('S' * 999 + 'a', "<p>" + "S" * 999 + 'a' + "</p>"),
        ('S' * 1000 + 'a', "<p>" + "S" * 1000 + '...' + "</p>")])
    def test_long_posts_get_truncated(
            self, body, html, mydb, pyramid_config, pyramid_req):
        # Make the Homepage post really long
        pyramid_req.matchdict = {'postname': 'Page2', 'id': 2}
        pyramid_req.params = {'form.submitted': True, 'tags': 'tag2'}
        pyramid_req.params['body'] = body
        Post_modifying_views(pyramid_req).edit_post_POST()
        pyramid_req.params = {}
        pyramid_req.matchdict = {'tag_name': 'tag2'}
        response = fireblog.tags.tag_view(pyramid_req)
        post = response["posts"][0]

        assert post["html"] == html


class Test_tag_manager:

    def test_success(self, pyramid_config, pyramid_req):
        res = fireblog.tags.tag_manager(pyramid_req)
        assert res == dict(tags=[('tag1', 2), ('tag2', 1), ('tag3', 0)],
                           title='Tag manager',
                           save_url='http://example.com/tags')

    def test_POST_success(self, pyramid_config, pyramid_req):
        """Test deleting tag1 and renaming tag2 and not changing tag3."""
        pyramid_req.params['form.submitted'] = True
        pyramid_req.params['check-tag1'] = False
        pyramid_req.params['check-tag2'] = True
        pyramid_req.params['check-tag3'] = True
        pyramid_req.params['text-tag1'] = 'tag1'
        pyramid_req.params['text-tag2'] = 'tag22'
        pyramid_req.params['text-tag3'] = 'tag3'

        res = fireblog.tags.tag_manager(pyramid_req)
        assert res.location == 'http://example.com/tags'

        pyramid_req.params = {}
        res = fireblog.tags.tag_manager(pyramid_req)
        assert res == dict(tags=[('tag22', 1), ('tag3', 0)],
                           title='Tag manager',
                           save_url='http://example.com/tags')
