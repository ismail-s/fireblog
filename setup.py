import os
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()


requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'pyramid_persona',
    'pyramid_dogpile_cache',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'markdown',
    'arrow',
    'shortuuid',
    'webtest',
    'PyRSS2Gen',
    'alembic',
    'requests'
]

if __name__ == '__main__':
    setup(name='fireblog',
          version='0.0',
          description='fireblog',
          long_description=README + '\n\n' + CHANGES,
          classifiers=[
              "Programming Language :: Python",
              "Framework :: Pyramid",
              "Topic :: Internet :: WWW/HTTP",
              "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
          ],
          author='',
          author_email='',
          url='',
          keywords='web wsgi bfg pylons pyramid',
          packages=find_packages(),
          include_package_data=True,
          zip_safe=False,
          test_suite='fireblog',
          install_requires=requires,
          tests_require = [
            'pytest',
            'pytest-cov',
            'pytest-pep8',
          ],
          cmdclass = {'test': PyTest},
          entry_points="""\
      [paste.app_factory]
      main = fireblog:main
      [console_scripts]
      initialize_fireblog_db = fireblog.scripts.initializedb:main
      """,
          )
