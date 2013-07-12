# encoding: utf-8
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

import time

from Products.SQLAlchemyDA.da import types_mapping, LOG


def SQLAlchemyDA_query_patch(self, query_string, max_rows=None, query_data=None):
    """ *The* query() method as used by the internal ZSQL
        machinery.
    """
    c = self._wrapper.connection
    cursor = c.cursor()

    rows = []
    desc = None
    nselects = 0

    ts_start = time.time()

    for qs in [x for x in query_string.split('\0') if x]:

        LOG.debug(qs)
        if query_data:
            proxy = cursor.execute(qs, query_data)
        else:
            proxy = cursor.execute(qs)

        description = cursor.description

        if description is not None:
            nselects += 1

            if nselects > 1:
                raise ValueError("Can't execute multiple SELECTs within a single query")

            if max_rows:
                rows = cursor.fetchmany(max_rows)
            else:
                rows = cursor.fetchall()

            desc = description
            types_map = self._typesMap(proxy)

    LOG.debug('Execution time: %3.3f seconds' % (time.time() - ts_start))

    if desc is None:
        return [], []

    items = []
    for name, type_code, width, internal_size, precision, scale, null_ok in desc:

        items.append({'name': name,
                      'type': types_mapping.get(types_map.get(type_code, None), 's'),
                      'null': null_ok,
                      'width': width,
                      })

    return items, rows
