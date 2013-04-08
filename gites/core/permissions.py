# encoding: utf-8
"""
gites.core

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

from Products.CMFCore.permissions import setDefaultRoles


def initialize():
    ViewAdmin = "GDW: View Administration"
    setDefaultRoles(ViewAdmin, ('Manager', 'Site Administrator'))
