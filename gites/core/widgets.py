# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget, registerPropertyType
from AccessControl import ClassSecurityInfo


class DBReferenceWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({'macro': 'widget_dbreference',
                        'helper_js': ('widget_dbreference.js', ),
                        'table': 'hebergement',
                        'size': '',
                        'unique_column': 'heb_pk',
                        'allow_non_exact_match': True,
                        'default_columns': 'heb_nom',
                        'view_url': '/view_hebergement?heb_pk=$(uid)',
                        'viewable_columns': {'heb_nom': 'Nom'}})
    security = ClassSecurityInfo()
    security.declarePublic('getBaseQuery')

    def getBaseQuery(self, instance, field):
        """
        Return base query to use for content search
        """
        results = {}
        results['portal_type']=[]
        return results

registerWidget(DBReferenceWidget,
                title = 'DB reference widget',
                description= ('Render a popup to select a reference in a DB', ),
                used_for = ('Products.Archetypes.Field.LinesField', ))

registerPropertyType('table', 'string', DBReferenceWidget)
registerPropertyType('default_columns', 'string', DBReferenceWidget)
registerPropertyType('unique_column', 'string', DBReferenceWidget)
registerPropertyType('view_url', 'string', DBReferenceWidget)
registerPropertyType('viewable_columns', 'dictionary', DBReferenceWidget)
registerPropertyType('allow_non_exact_match', 'boolean', DBReferenceWidget)
