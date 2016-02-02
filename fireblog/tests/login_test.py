import pytest
import fireblog.login as login

pytestmark = pytest.mark.usefixtures("test_with_one_theme")


class Test_groupfinder:

    def test_success(self, persona_test_admin_login, pyramid_config):
        emails = ['id5489746@mockmyid.com', persona_test_admin_login['email']]
        for email in emails:
            res = login.groupfinder(email)
            assert res == ['g:admin']

    def test_failure(self, pyramid_config):
        fake_email = 'some_fake_address@example.com'
        res = login.groupfinder(fake_email)
        assert res == ['g:commenter']
