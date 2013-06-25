# -*- coding: utf-8 -*-

from Products.Five import BrowserView

from mobile.sniffer.detect import detect_mobile_browser
from mobile.sniffer.utilities import get_user_agent


class ResponsiveView(BrowserView):
    """
    """

    def isMobile(self):
        """
        """
        ua = get_user_agent(self.request)
        if ua and detect_mobile_browser(ua):
            return True
        return False
