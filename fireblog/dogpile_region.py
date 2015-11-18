from pyramid_dogpile_cache import get_region


# This is the dogpile_cache cache region.
try:
    region = get_region('')
except KeyError:
    # KeyError occurs when this module is directly imported before
    # fireblog:main is called. Basically, in the fireblog:main function,
    # pyramid_dogpile_cache plugin sets up dogpile.cache using settings
    # from the usual ini files. However, if this module is imported first,
    # then this setup doesn't happen. As a result, as a fallback in these
    # cases (atm only when tests are run, which is when we actually want
    # to check that the cache is correctly managed by the website) we use
    # the memory cache backend.
    # Note: as the tests use the memory backend, I have made it so that
    # the cache gets wiped after each test run. But this has meant the tests
    # now rely on being run against the memory backend.
    region = get_region('', backend='dogpile.cache.memory')
