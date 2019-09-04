// This script gets the different tariff set options and puts them in the tariff menu
var create_tariff_set_options = function(type){
    var Type  = type.charAt(0).toUpperCase() + type.slice(1)
    $.getJSON("/get_tariff_set_options/" + type, function(json){
            $('#' + type + '_tariff_sets').empty();
            $.each(json, function(i, obj){
                tariff_version_option =  '<li>' +
                                             '<input class=\"' + type + '_tariff_version menu_check_list\" type=\"checkbox\"' +
                                             'onclick=\"tariff_set_update_actions(event, this, \'' + Type + '\',\'' + obj + '\')\"' +
                                             'value=\'' + obj + '\'>' +
                                             '<div class=\"menu_check_list_label\">' + obj + '</div>' +
                                         '</li>'
                $('#' + type + '_tariff_sets').append($(tariff_version_option));
            });
            get_active_tariff_set_version(Type);
    });
}

var tariff_set_update_actions = function(event, div_that_got_clicked, type, version){
    update_check_list(event, div_that_got_clicked)
    if (type == "Network"){
        var chosen_version = get_tariff_set_option("network_tariff_version")
    } else {
        var chosen_version = get_tariff_set_option("retail_tariff_version")
    }
    reset_tariff_set(type, chosen_version)
}

var get_tariff_set_option = function(type){
    var chosen_tariff_set_option
    var options = $('.' + type)
    $.each(options, function(i, option){
        if ($(option).is(":checked")){
            tariff_set_option = $(option).attr('value')
        }
    });
    return tariff_set_option
}

var reset_tariff_set = function(type, version){

    console.log('tried_to_reset_tariffs')
    request_details = {'type': type,
                       'version': version}
    // Get the server to reset the active tariff file
    $.ajax({
        url: '/set_tariff_set_in_use',
        data: JSON.stringify(request_details),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            alert_user_if_error(data)
            if(type == 'Retail'){
                reset_tariff_options('retail_tariff_selection_panel');
            } else {
                reset_tariff_options('network_tariff_selection_panel');
            }
        }
    });
};

var update_tariff_data_sets = function(){
    $('#updating_tariffs').dialog({
        modal: true,
        buttons: {"OK": function(){$('#updating_tariffs').dialog('close')}}
    });
    $('#updating_tariffs p').text("Please wait . . .")
    // Get the server to check the ceem tariff api for a more recent set of tariffs.
    $.ajax({
        url: '/update_tariffs',
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            alert_user_if_error(data)
            create_tariff_set_options('network');
            create_tariff_set_options('retail');
            $('#updating_tariffs p').text(data['message'])
        }
    });
};

var get_active_tariff_set_version = function(type){
    request_details = {'type': type}
    $.ajax({
        url: '/get_active_tariff_version',
        data: JSON.stringify(request_details),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            alert_user_if_error(data)
            set_tariff_set_option_in_gui(type, data['version'])
            }
    });
};

var set_tariff_set_option_in_gui = function(type, version){
    var chosen_tariff_set = type + 'Tariffs_' + version
    if (type == "Network"){
        var options = $('.network_tariff_version')
    } else {
        var options = $('.retail_tariff_version')
    }
    $.each(options, function(i, option){
        if ($(option).attr('value') == chosen_tariff_set){
            $(option).prop('checked', true);
        }
    });
}

create_tariff_set_options('network');
create_tariff_set_options('retail');

