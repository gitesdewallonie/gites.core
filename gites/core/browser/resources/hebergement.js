jQuery(document).ready(function($) {

    $('#contacter-proprio a').prepOverlay(
        {
            subtype: 'ajax',
            filter: '#content-for-khevine>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info',
            cssclass: 'overlay-contact',
            formselector: 'form[name="contact-proprio"]',
            config: {
            onBeforeLoad : function (e) {
              $(".datepicker-widget").datepicker({
                                                   minDate: 0,
                                                   dateFormat: "dd/mm/yy",
                                                   showOn: "both",
                                                   buttonImage: "++theme++gites.theme/images/icon_calendrier.png",
                                                   buttonImageOnly: true,
                                                 });
            return true;
            }
        }
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
