import collective.cookiecuttr.browser.viewlet

# override cookiecuttr JS call to add new options (#6358)
collective.cookiecuttr.browser.viewlet.js_template = """
<script type="text/javascript">

    (function($) {
        $(document).ready(function () {
            if($.cookieCuttr) {
                $.cookieCuttr({cookieAnalytics: false,
                               cookieNotificationLocationBottom: true,
                               cookiePolicyLink: "%s",
                               cookieMessage: "%s",
                               cookieAcceptButtonText: "%s"
                               });
                }
        })
    })(jQuery);
</script>

"""
