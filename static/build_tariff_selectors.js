// This script gets the different load options and puts them in the load selector
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

var get_tariff_options =  function(){

    var current_options = {'#select_tariff_state': {},
                         '#select_tariff_provider': {},
                         '#select_tariff_type': {},
                         '#select_tariff': {}};

    for (var key in current_options) {
        if (current_options.hasOwnProperty(key)) {
            current_options[key] = $(key).val();
        }
    }

    $.ajax({
        url: '/tariff_options',
        data: JSON.stringify(current_options),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){update_tariff_options(data, current_options);}
    });
};

get_tariff_options();

$('.tariff_selectors').on('change', function() {
    get_tariff_options();
});