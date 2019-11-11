var check_for_synthetic_options_then_update_check_list = function(event, checked_item){
    // Check if there are any synthetic network load options.
    if($('#synthetic_network_load_options li').length > 0){
        // If there are then keep the synthetic network load option selected and deselect other options.
        update_check_list(event, checked_item)
    } else {
        // Warn the user that there are no synthetic network load options and reverse their change to the check list.
        $('#warning_dialog').dialog({
            modal: true,
            buttons: {"OK": function(){$('#warning_dialog').dialog('close')}}
        });
        var message = "There are no synthetic network load options that can be used. Please create one before " +
                      "selecting this option."
        $('#warning_dialog p').text(message)
        reverse_user_check(event, checked_item)
    }
}

var build_network_load_options = function(){
    // This script gets the different load options and puts them in the load selector
    $.getJSON("/network_load_names", function(json){
        $('#synthetic_network_load_options').empty()
        $.each(json, function(i, name){

            console.log(name)
            add_option_to_ui(name)
        });
    });
}

var add_option_to_ui = function(option_name){
//    option_name = data['name']
    var option_template = '<li><input class=\"synthetic_network_load_option menu_check_list\" type=\"checkbox\"' +
                          'value=\"{}\" onclick=\"update_check_list(event, this)\"><div class="menu_check_list_label">{}</div></li>'
    var option_with_name = option_template.replace(/{}/g, option_name)
    $('#synthetic_network_load_options').append($(option_with_name))
    var synthetic_options = $('.synthetic_network_load_option');
    $.each(synthetic_options, function(i, option){
       if ($(option).val() == option_name){
           $(option).trigger('click');
       }
    })
}

build_network_load_options();
