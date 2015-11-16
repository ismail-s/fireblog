from collections.abc import MutableMapping
from fireblog.dogpile_region import region
from fireblog.models import DBSession, Settings
from .mapping import mapping


class _settings_dict(MutableMapping):
    @staticmethod
    def _get_item_from_db(key):
        '''Try and get 'key' from the settings table in the db, else raise a
        :py:exception:`KeyError`'''
        res = DBSession.query(Settings).filter_by(name=key).first()
        if not res:
            msg = '{} does not exist in the settings table'
            raise KeyError(msg.format(key))
        return res

    @region.cache_on_arguments()
    def __getitem__(self, key):
        res = self._get_item_from_db(key)
        # Cast the value
        for entry in mapping:
            if entry.registry_name == key:
                return entry.type(res.value)
        # If there is no corresponding registry entry, we just return rather
        # than crashing things.
        # TODO-log an error here
        return res.value

    def __setitem__(self, key, value):
        try:
            res = self._get_item_from_db(key)
            res.value = value
        except KeyError:
            new_entry = Settings(name=key, value=value)
            DBSession.add(new_entry)
        finally:
            DBSession.flush()
            self.__getitem__.set(value, self, key)

    def __delitem__(self, key):
        res = self._get_item_from_db(key)
        DBSession.delete(res)
        DBSession.flush()
        self.__getitem__.invalidate(self, key)

    def __iter__(self):
        names = DBSession.query(Settings.name).all()
        return (n.name for n in names)

    def __len__(self):
        return DBSession.query(Settings).count()

# Technically, everyone could use their own instance of _settings, but it is
# easier to not have to keep instantiating it.
settings_dict = _settings_dict()
