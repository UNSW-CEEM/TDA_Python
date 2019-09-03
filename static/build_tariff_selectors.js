// This script is responsible for updating the tariff selection drop downs

// This functions takes a set of options to populate the drop downs with,
// it also resets the selected values based on a set of currently selected values
var update_tariff_options = function(parent_id, options_by_type, current_options){
        $.each(options_by_type, function(option_type, options){
            option_identifier = '#' + parent_id + ' ' + option_type
            $(option_identifier).empty();
            if (option_type == '.select_tariff'){
                $(option_identifier).append($('<option>').text("None"));
            } else {
                $(option_identifier).append($('<option>').text("Any"));
            }
            $.each(options, function(i, option){
                    $(option_identifier).append($('<option>').text(option));
            });
            $(option_identifier).val(current_options[option_type]);
        });
};

// This function asks the server for possible tariff options given the current
// options already selected, it then updates the drop downs.
var get_tariff_options =  function(parent_id){
    // Get the current state of the drop downs.
    var current_options = {'.select_tariff_state': {},
                           '.select_tariff_provider': {},
                           '.select_tariff_type': {},
                           '.select_tariff': {}};

    for (var key in current_options) {
        if (current_options.hasOwnProperty(key)) {
            current_options[key] = $(key).val();
        }
    }

    // Put request details in single object.
    request_details = {'tariff_panel': parent_id, 'current_options': current_options}

    // Ask the server what the options should be now.
    $.ajax({
        url: '/tariff_options',
        data: JSON.stringify(request_details),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        // Call the function to update the drop downs with the new options.
        success: function(data){
            alert_user_if_error(data);
            update_tariff_options(parent_id, data['tariff_options'], current_options);
            }
    });
};

var reset_tariff_options = function(parent_id){
    $('#' + parent_id + ' .select_tariff_provider').val('Any');
    $('#' + parent_id + ' .select_tariff_state').val('Any');
    $('#' + parent_id + ' .select_tariff_type').val('Any');
    $('#' + parent_id + ' .select_tariff').val('None');
    $('#' + parent_id + ' .name_value').html('N/A');
    $('#' + parent_id + ' .type_value').html('N/A');
    $('#' + parent_id + ' .state_value').html('N/A');
    get_tariff_options(parent_id);
    tear_down_tables_in_tariff_type_panel(parent_id);
    $('#' + parent_id + ' .component_adder').hide();
}
