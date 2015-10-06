import pytest
import fireblog


class Test_groupfinder:

    def test_success(self, persona_test_admin_login,
                     pyramid_config, pyramid_req):
        emails = ['id5489746@mockmyid.com', persona_test_admin_login['email']]
        for email in emails:
            res = fireblog.groupfinder(email, pyramid_req)
            assert res == ['g:admin']

    def test_failure(self, pyramid_config, pyramid_req):
        fake_email = 'some_fake_address@example.com'
        res = fireblog.groupfinder(fake_email, pyramid_req)
        assert res == ['g:commenter']


class Test_getusername:

    @pytest.mark.parametrize('email, username', [
        ('id5489746@mockmyid.com', 'id5489746'),
        ('commenter@example.com', 'commenter')
    ])
    def test_success(self, pyramid_config, email, username):
        assert fireblog.get_username(email) == username

    def test_failure(self, pyramid_config):
        assert fireblog.get_username('nonexistentemail@example.com') == ''
