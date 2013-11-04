# -*- coding: utf-8 -*-
from sqlalchemy import func
from affinitic.caching.memcached import memcachedClient

from gites.db import session as DBSession
from gites.db.content import Hebergement
from gites.core.scripts.db import initializeDB
import gites.core.scripts


def main():
    initializeDB(gites.core.scripts)
    updateHebsSortOrder()


def updateHebsSortOrder():
    session = DBSession()

    query = session.query(Hebergement).join('app')
    query = query.order_by(func.random())

    position = 1
    for heb in query.all():
        heb.app.heb_app_sort_order = position
        session.add(heb)
        position += 1

    session.commit()
    session.flush()

    memcache = memcachedClient()
    memcache.invalidateAll()


if __name__ == "__main__":
    main()
