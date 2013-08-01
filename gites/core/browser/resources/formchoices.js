jQuery(document).ready(function($) {

    function toggleCheckboxes(name) {
        checkedInputs = $("input[name='" + name + "']:checked");
        if (checkedInputs.length == 1) {
            checkedInputs.prop('disabled', true);
        }
        else {
            checkedInputs.prop('disabled', false);
        }
    }

    toggleCheckboxes('form.widgets.hebergementType:list');

    $("input[name='form.widgets.hebergementType:list']").change(function(sender) {
        toggleCheckboxes('form.widgets.hebergementType:list');
    });


    // 'From' and 'To' dates should limit each other
    $("#form-widgets-fromDate").datepicker('option', 'onSelect', function(date) {
        $("#form-widgets-toDate").datepicker("option", "minDate", date);
    });
    $("#form-widgets-toDate").datepicker('option', 'onSelect', function(date) {
        $("#form-widgets-fromDate").datepicker("option", "maxDate", date);
    });

});
