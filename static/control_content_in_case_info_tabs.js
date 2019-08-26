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

var get_and_display_case_wholesale_price_info = function(case_name){
    // Get tariff info for case.
    $.ajax({
        url: '/get_wholesale_price_info',
        data: JSON.stringify(case_name),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        // Call the function to display the selected tariffs info
        success: function(data){
            if (typeof data !== 'string' &&  !(data instanceof String)){
                display_case_wholesale_price_info(case_name, data);
            }
            },
        error: function(a,b,c){console.log(b); console.log(c);}
    });
}

var display_case_wholesale_price_info = function(case_name, wholesale_price_info){
    $('#wholesale_price_case').text(case_name);
    $('#wholesale_price_year').text(wholesale_price_info['year'].toString());
    $('#wholesale_price_state').text(wholesale_price_info['state']);
    $("#info_wholesale_price_summary_labels").css("display", "block");
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
        $('#demog_info').append($('<div class="label_close_stacked">').text("Case: " + case_name));
        $.each(demo_options, function(name, option_chosen){
                $('#demog_info').append($('<div class="label_close_stacked">').text(name + ": " + option_chosen));
        });
}

var update_info_tabs_on_case_delete = function(case_name){
    // If the case being delete had its info displayed, then change the display info to another case.
    // If there are no other cases then clear the info tabs.

    if ($('#load_info_case').text() == case_name){
        // Clear info
        clear_all_case_info();
        // Get list of cases.
        case_controllers = $("#case_list .case_label")
        if (case_controllers.length >= 1){
            // If there are other cases then display the info for the first one.
            reset_case_info(case_controllers[0].innerHTML);
        } else {
            // Update menu bar status indicator
            $('#results_status_not_set').show()
            $('#results_status_set').hide()
        }
    }

}

var clear_all_case_info = function(){
    // Remove table displaying tariff info.
    // Get a list of the tables currently on display
    var current_tables = $('.case_area .tariff_table')
    // Tear down all the current tables.
    $.each(current_tables, function(index, table){
        tear_down_current_table(table, true)
    })
    // Delete remaining html
    $('#retail_info').empty();
    $('#network_info').empty();
    // Stop display info summaries
    $(".info_tariff_summary_labels").css("display", "none");
    $("#info_load_summary_labels").css("display", "none");
    $("#info_wholesale_price_summary_labels").css("display", "none");
    $("#demog_info").empty();
}

var reset_case_tariff_info_from_button = function(info_button){
    var case_name = $(info_button).attr('value');
    reset_case_info(case_name);
}

var reset_case_info = function(case_name){
    clear_all_case_info();
    get_and_display_case_tariff_info(case_name, 'retail');
    get_and_display_case_tariff_info(case_name, 'network');
    get_and_display_case_load_info(case_name);
    get_and_display_case_demo_info(case_name);
    get_and_display_case_wholesale_price_info(case_name);
}

var get_and_display_case_tariff_info = function(case_name, tariff_type){
    // Get tariff info for case.
    $.ajax({
        url: '/get_case_tariff',
        data: JSON.stringify({'case_name': case_name, 'tariff_type': tariff_type + '_tariff_selection_panel'}),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        // Call the function to display the selected tariffs info
        success: function(data){
            // If the tariff data is just a string that means no tariff of the correct type was found.
            // There for do not try and display data for this tariff
            if (typeof data !== 'string' &&  !(data instanceof String)){
                display_case_tariff_info(case_name, data, tariff_type);
            }
        },
        error: function(a,b,c){console.log(b); console.log(c);}
    });
}

var display_case_tariff_info = function(case_name, tariff_data, tariff_type){
    if (tariff_type == 'network'){
        var component = 'NUOS';
    } else {
        var component = 'Retail';
    }
    display_tables(tariff_type + '_info', tariff_type + '_info', tariff_data['Parameters'][component], false);
    var tariff_type_id = '#' + tariff_type + '_tariff_info'
    $(tariff_type_id + ' .tariff_info_case').text(case_name);
    $(tariff_type_id + ' .tariff_info_name').text(tariff_data['Name']);
    $(tariff_type_id + ' .tariff_info_type').text(tariff_data['Type']);
    $(tariff_type_id + ' .tariff_info_state').text(tariff_data['State']);
    $(tariff_type_id + ' .tariff_info_component').text(component);
    $(tariff_type_id + ' .tariff_info_daily_charge').text(tariff_data['Parameters'][component]['Daily']['Value']);
    $(tariff_type_id + " .info_tariff_summary_labels").css("display", "block");
}