jQuery(document).ready(function($) {

    var loadDatePicker = function() {
      $(".datepicker-widget").datepicker({
                                           minDate: 0,
                                           dateFormat: "dd/mm/yy",
                                           showOn: "both",
                                           buttonImage: "++theme++gites.theme/images/icon_calendrier.png",
                                           buttonImageOnly: true
                                         });

      $("#fromDate").datepicker('option', 'onSelect', function(date) {
          $("#toDate").datepicker("option", "minDate", date);
      });

      $("#toDate").datepicker('option', 'onSelect', function(date) {
          $("#fromDate").datepicker("option", "maxDate", date);
      });
    };

    $('#contacter-proprio a').prepOverlay(
        {
            subtype: 'ajax',
            filter: '#content-for-khevine>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info',
            cssclass: 'overlay-contact',
            formselector: 'form[name="contact-proprio"]',
            beforepost: function(form, form_data) {
              $(form).closest('#content-core')
                     .load(form.attr('action') + " #contact-proprio-formulaire",
                           form_data,
                           function(e) {
                loadDatePicker();
              });
            },
            config: {
              onBeforeLoad : function (e) {
                loadDatePicker();
              },
              mask: {color: '#000',
                       opacity: 0.4,
                       loadSpeed:0,
                       closeSpeed:0},
              color: '#ebecff',
              loadSpeed: 200,
              opacity: 0.9
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

    /*
    $('#afficher-groupement-heb a').prepOverlay(
        {
            subtype: 'ajax',
            filter: '#content-for-khevine>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info',
            closeselector: '[name=cancel]',
            noform: 'close'config: {
                fixed: false,
                speed: 'fast',
                mask: {color: '#000',
                       opacity: 0.4,
                       loadSpeed:0,
                       closeSpeed:0},
                color: '#ebecff',
                loadSpeed: 200,
                opacity: 0.9
            }
        }
    );
    */

});
