# -*- coding: utf-8 -*-
from zope.deferredimport import deprecated

deprecated('Please import cache decorator from affinitic.caching',
           cache='affinitic.caching:cache')
