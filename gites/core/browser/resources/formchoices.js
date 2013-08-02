jQuery(document).ready(function($) {

    // 'From' and 'To' dates should limit each other
    $("#form-widgets-fromDate").datepicker('option', 'onSelect', function(date) {
        $("#form-widgets-toDate").datepicker("option", "minDate", date);
    });
    $("#form-widgets-toDate").datepicker('option', 'onSelect', function(date) {
        $("#form-widgets-fromDate").datepicker("option", "maxDate", date);
    });

});
