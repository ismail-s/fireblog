import pytest
import fireblog.tags
from pyramid.httpexceptions import HTTPNotFound
from fireblog.models import DBSession


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
            # TODO-check that long posts are truncated correctly

    def test_failure(self, pyramid_config, pyramid_req):
        pyramid_req.matchdict['tag_name'] = 'doesntexist'
        response = fireblog.tags.tag_view(pyramid_req)
        assert isinstance(response, HTTPNotFound)


class Test_tag_manager:

    def test_success(self, pyramid_config, pyramid_req):
        res = fireblog.tags.tag_manager(pyramid_req)
        assert res == dict(tags=[('tag1', 2), ('tag2', 1)],
                           title='Tag manager',
                           save_url='http://example.com/tags')

    def test_POST_success(self, pyramid_config, pyramid_req):
        """Test deleting tag1 and renaming tag2."""
        pyramid_req.params['form.submitted'] = True
        pyramid_req.params['check-tag1'] = False
        pyramid_req.params['check-tag2'] = True
        pyramid_req.params['text-tag1'] = 'tag1'
        pyramid_req.params['text-tag2'] = 'tag22'

        # I'm not fully sure why we do this. But it works and stops issues
        # with autoflush and whatnot.
        # But in production it seems to be ok...
        DBSession.begin(subtransactions=True)
        res = fireblog.tags.tag_manager(pyramid_req)
        DBSession.commit()
        assert res.location == 'http://example.com/tags'

        pyramid_req.params = {}
        res = fireblog.tags.tag_manager(pyramid_req)
        assert res == dict(tags=[('tag22', 1)],
                           title='Tag manager',
                           save_url='http://example.com/tags')
