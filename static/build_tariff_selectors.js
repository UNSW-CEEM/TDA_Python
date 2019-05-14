// This script is responsible for updating the tariff selection drop downs

// This functions takes a set of options to populate the drop downs with,
// it also reset the selected values based on a set of currently selected values
var update_tariff_options = function(options_by_type, current_options){
        $.each(options_by_type, function(option_type, options){
            $(option_type).empty();
            $(option_type).append($('<option>').text("Select1"));
            $.each(options, function(i, option){
                    $(option_type).append($('<option>').text(option));
            });
            $(option_type).val(current_options[option_type]);
        });
};

// This function asks the server for possible tariff options given the current
// options already selected, it then updates the drop downs.
var get_tariff_options =  function(){

    // Get the current state of the drop downs.
    var current_options = {'#select_tariff_state': {},
                         '#select_tariff_provider': {},
                         '#select_tariff_type': {},
                         '#select_tariff': {}};
    for (var key in current_options) {
        if (current_options.hasOwnProperty(key)) {
            current_options[key] = $(key).val();
        }
    }

    // Ask the server what the options should be now.
    $.ajax({
        url: '/tariff_options',
        data: JSON.stringify(current_options),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        // Call the function to update the drop downs with the new options.
        success: function(data){update_tariff_options(data, current_options);}
    });
};

// Get the options when the app first starts.
get_tariff_options();

// Get the options every time someone updates a tariff drop down.
$('.tariff_filter').on('change', function() {
    get_tariff_options();
});