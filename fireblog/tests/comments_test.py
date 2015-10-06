import fireblog.comments
import fireblog.utils
from fireblog.events import RenderingPost
from fireblog.models import DBSession, Post
import datetime

try:
    import unittest.mock as mock
    # unittest.mock was added in python3
except ImportError:
    import mock


class Test_comment_view:

    @staticmethod
    def get_comment_list(postname, pyramid_req):
        post = DBSession.query(Post).filter_by(name=postname).first()
        event = RenderingPost(post, pyramid_req)
        return fireblog.comments.render_comments_list_from_event(event)

    def test_success(self, pyramid_config, pyramid_req):
        res = self.get_comment_list('Homepage', pyramid_req)
        expected_comment = {
            'created': '01 Jan 2014',
            'author': 'id5489746',
            'comment': 'test comment',
            'uuid': 'comment1-uuid'}
        assert len(res) == 1
        assert res[0] == expected_comment


class Test_comment_add:

    def test_anon_success(self, pyramid_config, pyramid_req):
        comment = 'A test comment...'
        pyramid_req.params['postname'] = 'Page2'
        pyramid_req.params['comment'] = comment
        pyramid_req.params['form.submitted'] = True
        with mock.patch('requests.post', autospec=True) as mock_requests_post:
            mock_response = mock.Mock()
            mock_response.json.return_value = {'success': True}
            mock_requests_post.return_value = mock_response
            res = fireblog.comments.comment_add(pyramid_req)
        assert res.location == 'http://example.com/posts/Page2'

        pyramid_req.params = {}
        comments_list = Test_comment_view.get_comment_list(
            'Page2', pyramid_req)
        assert len(comments_list) == 1
        comment_res = comments_list[0]
        assert comment_res['author'] == 'anonymous'
        assert comment_res['comment'] == comment
        assert comment_res['uuid']
        # TODO-assert about when comment was created-use freezegun

    def test_logged_in_success(self, pyramid_config, pyramid_req):
        comment = 'A test comment...'
        pyramid_req.params['postname'] = 'Page2'
        pyramid_req.params['comment'] = comment
        pyramid_req.params['form.submitted'] = True
        pyramid_config.testing_securitypolicy(
            userid='id5489746@mockmyid.com', permissive=True)
        res = fireblog.comments.comment_add(pyramid_req)
        assert res.location == 'http://example.com/posts/Page2'

        pyramid_req.params = {}
        comments_list = Test_comment_view.get_comment_list(
            'Page2', pyramid_req)
        assert len(comments_list) == 1
        comment_res = comments_list[0]
        assert comment_res['author'] == 'id5489746'
        assert comment_res['comment'] == comment
        assert comment_res['uuid']
        # TODO-assert about when comment was created...


class Test_comment_delete:

    def test_success(self, pyramid_config, pyramid_req):
        pyramid_req.params['comment-uuid'] = 'comment1-uuid'
        pyramid_req.params['postname'] = 'Homepage'
        res = fireblog.comments.comment_delete(pyramid_req)
        assert res.location == 'http://example.com/posts/Homepage'

        comments_list = Test_comment_view.get_comment_list(
            'Homepage', pyramid_req)
        assert comments_list == []
