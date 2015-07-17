import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
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
    'ago',
    'shortuuid',
    'webtest',
    'pytest',
    'PyRSS2Gen',
    'alembic',
    'requests'
    ]

setup(name='myblog',
      version='0.0',
      description='myblog',
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
      test_suite='myblog',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = myblog:main
      [console_scripts]
      initialize_myblog_db = myblog.scripts.initializedb:main
      """,
      )
