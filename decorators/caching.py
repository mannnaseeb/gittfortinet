import logging
import functools
from flask import current_app
from caching import cache
from fortinet_common.api import APIResponse
from utils.fortinet_api_logger import FortinetAPILogger


logger = FortinetAPILogger(logging.getLogger('gunicorn.error'))
class CacheManager:
    """Cache Manager"""
    def cached(self,class_name, key, pk=None, timeout=None):

        def decorator(f):
            @functools.wraps(f)
            def decorated_func(*args, **kwargs):
                _class_name = ""
                if callable(class_name):
                    _class_name = class_name(*args, **kwargs)
                else:
                    _class_name = class_name

                def __set_data__(data_list):
                    data_map = {_class_name + data[key]: data for data in data_list}
                    if timeout and isinstance(timeout, int):
                        cache.set_many(data_map, timeout=timeout)
                    else:
                        cache.set_many(data_map)
                    return data_map

                if pk:
                    id = kwargs.pop(pk, None)
                else:
                    id = kwargs.pop('id', None)
                if id:
                    data = cache.get(_class_name+id)
                    if not data:
                        logger.debug(f"cache miss for key '{_class_name+id}'")
                        rv = f(*args, **kwargs)
                        if rv.status == 200 and rv.data:
                            data_map = __set_data__(rv.data['data'])
                            rv = APIResponse(data={'data': [data_map[_class_name+id]],
                             'count': 1}, status=200)
                    else:
                        logger.debug(f"cache hit for key '{_class_name+id}'")
                        rv = APIResponse(data={'data': [data], 'count': 1}, status=200)
                else :
                    cache_key_prefix = current_app.config.get('CACHE_KEY_PREFIX')
                    key_pattern = cache_key_prefix + _class_name + "*"
                    binary_keys = cache.cache._read_clients.keys(key_pattern)
                    if not binary_keys:
                        # cache miss
                        # return value must be a list data structure
                        logger.debug(f"cache miss for key '{key_pattern}'")
                        rv = f(*args, **kwargs)
                        if rv.status == 200 and rv.data:
                            data_map = __set_data__(rv.data['data'])
                    else:
                        # cache hit
                        logger.debug(f"cache hit for key '{key_pattern}'")
                        keys = [k.decode("utf-8", errors="ignore").replace(cache_key_prefix, '') for k in binary_keys if k]
                        cached_data = cache.get_many(*keys)
                        rv = APIResponse(data={'data': cached_data,
                         'count': len(cached_data)}, status=200)
                return rv

            return decorated_func

        return decorator
