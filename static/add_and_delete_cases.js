var add_case = function(){
    // Get the active component tab when the add case button was clicked.
    var component = get_active_network_component();

    // Get the name of the selected tariff.
    case_name = $('#case_name').val();

    // Get the name of the selected tariff.
    network_tariff_name = $('#network_tariff_selection_panel' + ' .select_tariff').val();

    // Get load details
    load_request = get_load_details_from_ui();

    // Bundle case details into a single object
    case_details = {'case_name': case_name,
                    'tariff_name': network_tariff_name,
                    'component': component,
                    'load_details': load_request};

    $('#case_namer').dialog('close');
    $('#dialog').dialog({modal: true});
    // Get the python app to create the case and calculate results, after this is done create the result plots.
    $.ajax({
        url: '/add_case',
        data: JSON.stringify(case_details),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            plot_results();
            get_and_display_case_tariff_info(case_name);
            get_and_display_case_load_info(case_name);
            get_and_display_case_demo_info(case_name);
            }
    });
}

var delete_case = function(delete_button){
    var case_name = $(delete_button).attr('value')
    var case_name_no_spaces = case_name.replace(/\s/g, '');

    // Delete case controller
    $('#' + case_name_no_spaces).remove();

    // Delete case on python side.
    $.ajax({
        url: '/delete_case',
        data: JSON.stringify(case_name),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json"
    });

    // Re plot charts
    plot_results();

    //update case info tabs
    update_info_tabs_on_case_delete(case_name);

}