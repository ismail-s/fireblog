import pytest
import fireblog

pytestmark = pytest.mark.usefixtures("test_with_one_theme")


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
        res = fireblog.get_secret_settings(filename, defaults={'d': '3'})
        assert res == {'d': '3', 'test': '31'}

    def test_returns_empty_dict_when_no_filename_passed(self):
        assert fireblog.get_secret_settings(None) == {}
