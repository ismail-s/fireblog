from fireblog.compat import MutableMapping
from fireblog.dogpile_region import region
from fireblog.models import DBSession, Settings
from .mapping import mapping
import logging


log = logging.getLogger(__name__)


class _settings_dict(MutableMapping):

    @staticmethod
    def _get_item_from_db(key):
        '''Try and get 'key' from the settings table in the db, else raise a
        :py:exception:`KeyError`'''
        res = DBSession.query(Settings).filter_by(name=key).first()
        if not res:
            log.info('Failed to find settings item {} in db'.format(key))
            msg = '{} does not exist in the settings table'
            raise KeyError(msg.format(key))
        return res

    @region.cache_on_arguments()
    def __getitem__(self, key):
        try:
            res = self._get_item_from_db(key)
        except KeyError:
            res = None
        # Cast the value
        for entry in mapping:
            if entry.registry_name == key:
                if res:
                    return entry.type(res.value)
                else:
                    return entry.type(entry.default_value)
        # If there is no corresponding registry entry, we log and raise an
        # error. Tests should prevent this code ever being hit in production...
        log.error('The settings value {} was attempted to be obtained, '
                  'despite it not being an official settings entry in '
                  'the mapping'.format(key))
        raise KeyError

    def __setitem__(self, key, value):
        try:
            res = self._get_item_from_db(key)
            log.info(
                'Settings item {} has been changed from {} to {}.'.format(
                    key, res.value, value))
            res.value = value
        except KeyError:
            new_entry = Settings(name=key, value=value)
            DBSession.add(new_entry)
            log.info('Settings item {} has been added.'.format(key))
        finally:
            DBSession.flush()
            self.__getitem__.set(value, self, key)

    def __delitem__(self, key):
        res = self._get_item_from_db(key)
        DBSession.delete(res)
        log.info('Settings item {} has been deleted.'.format(key))
        DBSession.flush()
        self.__getitem__.invalidate(self, key)

    def __iter__(self):
        registry_names = []
        for entry in mapping:
            registry_names.append(entry.registry_name)
            yield registry_names[-1]
        settings = DBSession.query(Settings.name).all()
        for n in settings:
            # Avoid returning the same key multiple times
            if n.name not in registry_names:
                yield n.name

    def __len__(self):
        return DBSession.query(Settings).count()

# Technically, everyone could use their own instance of _settings, but it is
# easier to not have to keep instantiating it.
settings_dict = _settings_dict()
