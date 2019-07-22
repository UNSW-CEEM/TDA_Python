var get_and_display_case_load_info = function(case_name){
    // Get tariff info for case.
    $.ajax({
        url: '/get_case_load',
        data: JSON.stringify(case_name),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        // Call the function to display the selected tariffs info
        success: function(data){display_case_load_info(case_name, data);},
        error: function(a,b,c){console.log(b); console.log(c);}
    });
}

var display_case_load_info = function(case_name, load_info){
    $('#load_info_case').text(case_name);
    $('#load_info_n_users').text(load_info['n_users'].toString());
    $('#load_info_database').text(load_info['database']);
    $("#info_load_summary_labels").css("display", "block");
}

var get_and_display_case_demo_info = function(case_name){
    // Get tariff info for case.
    $.ajax({
        url: '/get_case_demo_options',
        data: JSON.stringify(case_name),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        // Call the function to display the selected tariffs info
        success: function(data){display_case_demo_info(case_name, data);},
        error: function(a,b,c){console.log(b); console.log(c);}
    });
}

var display_case_demo_info = function(case_name, demo_options){
        $("#demog_info").empty();
        $('#demog_info').append($('<div>').text(case_name));
        $.each(demo_options, function(name, option_chosen){
                $('#demog_info').append($('<div>').text(name + ": " + option_chosen));
        });
}

var update_info_tabs_on_case_delete = function(case_name){
    // If the case being delete had its info displayed, then change the display info to another case.
    // If there are no other cases then clear the info tabs.

    if ($('#tariff_info_case').text() == case_name){
        // Get list of cases.
        case_controllers = $("#case_list .case_label")

        if (case_controllers.length < 1){
            // If there are no case with info to display.
            // Remove table displaying tariff info.
            tear_down_current_table('info', true);
            // Stop display info summaries
            $("#info_tariff_summary_labels").css("display", "none");
            $("#info_load_summary_labels").css("display", "none");
            $("#demog_info").empty();
        } else {
            // If there are other cases then display the info for the first one.
            get_and_display_case_tariff_info(case_controllers[0].innerHTML);
            get_and_display_case_load_info(case_controllers[0].innerHTML);
            get_and_display_demo_info(case_controllers[0].innerHTML);
        }
    }

}

var reset_case_tariff_info_from_button = function(info_button){
        var case_name = $(info_button).attr('value');
        get_and_display_case_tariff_info(case_name);
        get_and_display_case_load_info(case_name);
        get_and_display_case_demo_info(case_name);
}

var get_and_display_case_tariff_info = function(case_name){
    // Get tariff info for case.
    $.ajax({
        url: '/get_case_tariff',
        data: JSON.stringify(case_name),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        // Call the function to display the selected tariffs info
        success: function(data){display_case_tariff_info(case_name, data);},
        error: function(a,b,c){console.log(b); console.log(c);}
    });
}

var display_case_tariff_info = function(case_name, tariff_data){
    component = Object.keys(tariff_data['Parameters'])[0];
    display_table_data('info', tariff_data['Parameters'][component], true);
    $('#tariff_info_case').text(case_name);
    $('#tariff_info_name').text(tariff_data['Name']);
    $('#tariff_info_type').text(tariff_data['Type']);
    $('#tariff_info_state').text(tariff_data['State']);
    $('#tariff_info_component').text(component);
    $('#tariff_info_daily_charge').text(tariff_data['Parameters'][component]['Daily']['Value']);
    if ('Energy' in tariff_data['Parameters'][component]){
        $('#tariff_info_energy_charge').text(tariff_data['Parameters'][component]['Energy']['Value']);
    } else {
        $('#tariff_info_energy_charge').text('')
    }
    $("#info_tariff_summary_labels").css("display", "block");
}