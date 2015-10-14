import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

with open(os.path.join(here, 'requirements.txt')) as f:
    requires = f.read().split('\n')


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
          entry_points="""\
      [paste.app_factory]
      main = fireblog:main
      [console_scripts]
      initialize_fireblog_db = fireblog.scripts.initializedb:main
      """,
          )
