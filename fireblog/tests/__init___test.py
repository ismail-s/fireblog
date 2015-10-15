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


class Test_get_secret_settings:

    @staticmethod
    def create_test_file(tmpdir, content):
        p = tmpdir.join("test.ini")
        p.write(content)
        return str(p)

    def test_success_no_defaults(self, tmpdir):
        content = '''
[DEFAULT]
test = 1
test.2 = two
'''
        filename = self.create_test_file(tmpdir, content)
        res = fireblog.get_secret_settings(filename)
        assert res == {'test': '1', 'test.2': 'two'}

    def test_success_defaults(self, tmpdir):
        content = '''
[DEFAULT]
test = %(d)s1
'''
        filename = self.create_test_file(tmpdir, content)
        res = fireblog.get_secret_settings(filename, defaults={'d':'3'})
        assert res == {'d': '3', 'test': '31'}

    def test_returns_empty_dict_when_no_filename_passed(self):
        assert fireblog.get_secret_settings(None) == {}
