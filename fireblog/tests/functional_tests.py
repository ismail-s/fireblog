import pytest
from webtest.app import AppError
import contextlib
import re


class Test_functional_tests:

    def get_csrf_token(self, testapp):
        res = testapp.get('http://localhost/')
        return re.search(r"csrf_token: '(?P<token>[a-zA-Z0-9]+)'",
                         str(res.html)).group('token')

    def login(self, testapp, persona_test_admin_login):
        assertion = persona_test_admin_login['assertion']
        csrf_token = self.get_csrf_token(testapp)
        viewer_login = '/login?csrf_token={}'.format(csrf_token)
        return testapp.post(viewer_login, dict(assertion=assertion,
                                               came_from='/'))

    def logout(self, testapp):
        csrf_token = self.get_csrf_token(testapp)
        return testapp.post('/logout?csrf_token={}'.format(csrf_token),
                            dict(came_from='/'))

    @contextlib.contextmanager
    def logged_in(self, testapp, persona_test_admin_login):
        '''
        This is a context manager that provides a logged in session as admin.
        Use as follows:

            with logged_in(testapp):
                # Do stuff whilst logged in.
                pass
        '''
        self.login(testapp, persona_test_admin_login)
        try:
            yield
        finally:
            self.logout(testapp)

    def test_homepage(self, testapp):
        res = testapp.get('http://localhost/')
        page = str(res.html)
        assert res.status == '200 OK'
        assert '<h1>Page2</h1>' in page or\
            '<h1 class="center">Page2</h1>' in page
        assert '<p>This is page 2</p>' in page

    def test_get_page(self, testapp):
        res = testapp.get('http://localhost/posts/Page2')
        page = str(res.html)
        assert res.status == '200 OK'
        assert '<h1>Page2</h1>' in page or\
            '<h1 class="center">Page2</h1>' in page
        assert '<p>This is page 2</p>' in page
        found_comment_h2_elem = False
        for elem in res.html.find_all('h2'):
            if elem.string == 'Comments':
                found_comment_h2_elem = True
        assert found_comment_h2_elem
        found_comment_form_elem = False
        for elem in res.html.find_all('form'):
            if elem['id'] == 'add-comments':
                found_comment_form_elem = True
        assert found_comment_form_elem

    def test_get_all_page(self, testapp):
        res = testapp.get('http://localhost/all_posts')
        assert res.status == '200 OK'
        assert 'Homepage' in str(res.html)
        assert '<p>This is the front page</p>' in str(res.html)
        assert 'Page2' in str(res.html)
        assert '<p>This is page 2</p>' in str(res.html)

    def test_login(self, testapp, persona_test_admin_login):
        res = self.login(testapp, persona_test_admin_login)
        assert res.status == '200 OK'

        correct_res = {'success': True, 'redirect': '/'}
        assert res.json == correct_res
        self.logout(testapp)

    def test_logout(self, testapp):
        res = self.logout(testapp)
        assert res.status == '200 OK'
        assert res.json == {'redirect': '/'}

    def test_can_access_edit_pages_after_logging_in(
            self, testapp, persona_test_admin_login):
        with self.logged_in(testapp, persona_test_admin_login):
            res = testapp.get('/posts/Page2/edit')
            assert res.status == '200 OK'
            assert 'This is page 2' in str(res.html)

    def test_can_access_del_pages_after_logging_in(
            self, testapp, persona_test_admin_login):
        with self.logged_in(testapp, persona_test_admin_login):
            res = testapp.get('/posts/Page2/del')
            assert res.status == '200 OK'
            # TODO-add more checks over here maybe

    def test_can_access_add_pages_after_logging_in(
            self, testapp, persona_test_admin_login):
        with self.logged_in(testapp, persona_test_admin_login):
            res = testapp.get('/posts/some new page/add')
            assert res.status == '200 OK'
            assert 'some new page' in str(res.html)

    @pytest.mark.parametrize('url', ['/posts/Page2/edit',
                                     '/posts/Page2/del',
                                     '/posts/some new page/add',
                                     '/tags'])
    def test_cant_access_admin_pages_with_no_login(self, testapp, url):
        with pytest.raises(AppError) as exc_info:
            res = testapp.get(url)
        assert '403 Forbidden' in str(exc_info.value)

    def test_crud(self, theme, testapp, persona_test_admin_login):
        """Testing all CRUD operations in one big test."""
        if theme == 'polymer':
            pytest.skip("This test can't work with the js based form fields in"
                        "the polymer theme.")
        with self.logged_in(testapp, persona_test_admin_login):

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
            res = res.click(href=r'.*/edit')
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
            res = res.click(href=r'.*/del')
            form = res.forms["del-post"]
            res = form.submit('form.submitted')

            # 6. Test we get a 404 on trying to read the post
            with pytest.raises(AppError) as excinfo:
                res = testapp.get('/posts/some new page')
            assert '404 Not Found' in str(excinfo.value)

    def test_logout_changes_page_back_to_page_before_logging_in(
            self, testapp, persona_test_admin_login):
        '''
        This test covers a bug I introduced at one point when the view_post
        page was fully cached, after template rendering. This meant that the
        page would always be retrieved from cache, not taking into account
        things like logging in which means that person needs to see a different
        page.
        '''
        def get_page2_html:
            return testapp.get('http://localhost/posts/Page2').html
        unauthenticated_homepage = get_page2_html()
        with self.logged_in(testapp, persona_test_admin_login):
            authenticated_homepage = get_page2_html()
        unauthenticated_homepage_2 = get_page2_html()

        assert unauthenticated_homepage == unauthenticated_homepage_2
        assert authenticated_homepage != unauthenticated_homepage
