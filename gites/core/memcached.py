# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
import cPickle
import os
from zope.component import queryUtility
from zope.ramcache.interfaces.ram import IRAMCache
from lovely.memcached.interfaces import IMemcachedClient
from lovely.memcached.utility import MemcachedClient
from plone.memoize.ram import (AbstractDict, store_in_cache, RAMCacheAdapter)
from sqlalchemy.engine.base import RowProxy
from plone.memoize import volatile
import md5

DEPENDENCIES = {}


def memcachedClient():
    servers = os.environ.get(
        "MEMCACHE_SERVER", "127.0.0.1:11211").split(",")
    return MemcachedClient(servers, defaultNS=u'cerise',
                           defaultAge=86400)


class MemcacheAdapter(AbstractDict):

    def __init__(self, client, globalkey=''):
        self.client = client

        dependencies = []
        if globalkey:
            for k, v in DEPENDENCIES.items():
                if globalkey in v:
                    dependencies.append(k)

        self.dependencies = dependencies

    def _make_key(self, source):
        return md5.new(source).hexdigest()

    def __getitem__(self, key):
        cached_value = self.client.query(self._make_key(key), raw=True)
        if cached_value is None:
            raise KeyError(key)
        else:
            return cPickle.loads(cached_value)

    def __setitem__(self, key, value):
        try:
            cached_value = cPickle.dumps(value)
        except TypeError:
            if isinstance(value, list) and isinstance(value[0], RowProxy):
                value = [dict(d) for d in value]
            elif isinstance(value, RowProxy):
                value = dict(value)
            else:
                raise
            cached_value = cPickle.dumps(value)
        self.client.set(cached_value, self._make_key(key), raw=True,
                        dependencies=self.dependencies)

    def setWithLifetime(self, key, value, lifetime):
        cached_value = cPickle.dumps(value)
        self.client.set(cached_value, self._make_key(key), raw=True,
                        lifetime=lifetime,
                        dependencies=self.dependencies)


def choose_cache(fun_name):
    client = queryUtility(IMemcachedClient)
    if client is not None:
        return MemcacheAdapter(client, globalkey=fun_name)
    else:
        return RAMCacheAdapter(queryUtility(IRAMCache),
                               globalkey=fun_name)


_marker = object()


def cache(get_key, dependencies=None, lifetime=None):

    def decorator(fun):

        def replacement(*args, **kwargs):
            if dependencies is not None:
                for d in dependencies:
                    deps = DEPENDENCIES.get(d, [])
                    method = "%s.%s" % (fun.__module__, fun.__name__)
                    if method not in deps:
                        deps.append(method)
                        DEPENDENCIES[d] = deps
            try:
                key = get_key(fun, *args, **kwargs)
            except volatile.DontCache:
                return fun(*args, **kwargs)
            key = '%s.%s:%s' % (fun.__module__, fun.__name__, key)
            cache = store_in_cache(fun, *args, **kwargs)
            cached_value = cache.get(key, _marker)
            if cached_value is _marker:
                if lifetime is None:
                    cached_value = cache[key] = fun(*args, **kwargs)
                else:
                    cached_value = fun(*args, **kwargs)
                    cache.setWithLifetime(key, cached_value, lifetime)
            return cached_value
        return replacement
    return decorator
