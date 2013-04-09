jQuery(document).ready(function($) {

    $('#contacter-proprio a').prepOverlay(
        {
            subtype: 'ajax',
            filter: '#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info',
            cssclass: 'overlay-contact',
            formselector: 'form[name="contact-proprio"]'
        }
    );

});
