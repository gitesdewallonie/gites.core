jQuery(document).ready(function($) {

    $('#contacter-proprio a').prepOverlay(
        {
            subtype: 'ajax',
            filter: '#content-for-khevine>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info',
            cssclass: 'overlay-contact',
            formselector: 'form[name="contact-proprio"]'
        }
    );

    $('#signaler-un-probleme-button a').prepOverlay(
        {
            subtype: 'ajax',
            filter: '#content-for-khevine>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info',
            cssclass: 'overlay-signaler',
            formselector: 'form[name="signaler-probleme"]'
        }
    );

    $('.carousel').carousel({  
      interval: false
    })  

});
