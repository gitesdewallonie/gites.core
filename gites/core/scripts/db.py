# -*- coding: utf-8 -*-

from zope.component import getUtility
from zope.configuration import xmlconfig

from affinitic.db.interfaces import IDatabase
from affinitic.db.utils import initialize_declarative_mappers, initialize_defered_mappers

from gites.db import DeclarativeBase


def initializeDB(module):
    """
    Initialize db and mappers for script and return a session
    """
    parseZCML(module)
    pg = getUtility(IDatabase, 'postgres')
    session = pg.session
    initialize_declarative_mappers(DeclarativeBase, pg.metadata)
    initialize_defered_mappers(pg.metadata)
    return session


def parseZCML(package, file='configure.zcml'):
    context = xmlconfig._getContext()
    xmlconfig.include(context, 'configure.zcml', package)
    context.execute_actions()
