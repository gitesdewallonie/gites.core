# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName


def migrate(context):
    pm = getToolByName(context, 'portal_membership')
    acl = getToolByName(context, 'acl_users')
    for memberId in acl.ldap.enumerateUsers():
        memberId = memberId.get('cn')
        member = pm.getMemberById(memberId)
        editor = member.getProperty('wysiwyg_editor', None)
        if editor == 'TinyMCE':
            print('%s: TinyMCE already selected, leaving alone' % memberId)
        else:
            member.setMemberProperties({'wysiwyg_editor': 'TinyMCE'})
            print('%s: TinyMCE has been set' % memberId)
    return
