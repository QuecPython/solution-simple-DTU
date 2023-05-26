import ujson


class Settings(object):
    CONFIG_FILE_PATH = None
    __settings = None

    @classmethod
    def get(cls, key_string):
        return cls.__recurse_handler(
            cls.current_settings(),
            key_string.split('.'),
            operate='get'
        )

    @classmethod
    def set(cls, key_string, value):
        return cls.__recurse_handler(
            cls.current_settings(),
            key_string.split('.'),
            value=value,
            operate='set'
        )

    @classmethod
    def delete(cls, key_string):
        keys = key_string.split('.')
        return cls.__recurse_handler(
            cls.current_settings(),
            keys,
            operate='delete'
        )

    @classmethod
    def __recurse_handler(cls, settings, keys, value=None, operate=''):
        if len(keys) == 0:
            return

        if not isinstance(settings, dict):
            raise TypeError('config item \"{}\" is not a dict type.'.format(settings))

        key = keys.pop(0)

        if len(keys) == 0:
            if operate == 'get':
                rv = settings[key] if key in settings else None
                return rv
            elif operate == 'set':
                settings[key] = value
            elif operate == 'delete':
                del settings[key]
            return

        return cls.__recurse_handler(settings[key], keys, value=value, operate=operate)

    @classmethod
    def current_settings(cls):
        if cls.CONFIG_FILE_PATH is None:
            raise ValueError('you must set CONFIG_FILE_PATH.')

        if cls.__settings is None:
            cls.__settings = cls.__read_config()
        return cls.__settings

    @classmethod
    def set_config_path(cls, path):
        cls.CONFIG_FILE_PATH = path

    @classmethod
    def reload(cls):
        cls.__settings = None

    @classmethod
    def save(cls):
        with open(cls.CONFIG_FILE_PATH, 'w+', encoding='utf-8') as f:
            return ujson.dump(cls.__settings, f)

    @classmethod
    def __read_config(cls):
        with open(cls.CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            return ujson.load(f)
