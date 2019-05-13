// This script gets the different load options and puts them in the load selector
$.getJSON("/tariff_options", function(options_by_type){
        $.each(options_by_type, function(option_type, options){
            $(option_type).empty();
            $(option_type).append($('<option>').text("Select1"));
            $.each(options, function(i, option){
                    $(option_type).append($('<option>').text(option));
            });
        });
});
