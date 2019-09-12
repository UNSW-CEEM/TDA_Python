var add_case_to_python = function(){
    // Get the name of the selected tariff.
    var case_name = $('#case_name').val();

    // Get the name of the selected tariff.
    var retail_tariff_name = $('#retail_tariff_selection_panel .select_tariff').val();
    var network_tariff_name = $('#network_tariff_selection_panel .select_tariff').val();

    // Get load name

    var load_request = get_load_details_from_ui();

    // Get wholesale price details
    var year = $('#select_wholesale_year').val();
    var state = $('#select_wholesale_state').val();
    wholesale_price_details = {'year': year, 'state': state}

    // Bundle case details into a single object
    var case_details = {'case_name': case_name,
                        'retail_tariff_name': retail_tariff_name,
                        'network_tariff_name': network_tariff_name,
                        'load_details': load_request,
                        'wholesale_price_details': wholesale_price_details};

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
            alert_user_if_error(data)
            plot_results();
            reset_case_info(case_name);
            // Update menu bar status indicator
            $('#results_status_not_set').hide()
            $('#results_status_set').show()
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
        dataType:"json",
        success: function(data){alert_user_if_error(data)}
    });

    // Re plot charts
    plot_results();

    //update case info tabs
    update_info_tabs_on_case_delete(case_name);

}

var get_default_case_name = function(){
    // Get a un used case name to put as the default name in the case namer dialog box.
    $.ajax({
        url: '/get_case_default_name',
        contentType: 'application/json;charset=UTF-8',
        async: 'false',
        dataType:"json",
        success: function(data){
            alert_user_if_error(data);
            launch_case_namer(data['name']);
            }
    });
}


var launch_case_namer = function(default_name){
    $('#case_name').val(default_name)
    $( "#case_namer" ).dialog({
        modal: true,
        buttons: {"Save case": function(){add_case()}}
    });
}

var add_case = function(){
    case_name = $('#case_name').val();
    add_case_to_gui(case_name)
    add_case_to_python();
    update_single_case_selector();
}

var add_case_to_gui = function(case_name){
    case_name_no_spaces = case_name.replace(/\s/g, '');
    // Get a copy of the case control template.
    var $new_case_control = $('#case_control_template').clone();
    // Set the id of the copy equal to the case name.
    $new_case_control.attr('id', case_name_no_spaces);
    // Insert the copy into the case panel
    $('#case_list').append($new_case_control);
    // Make the case control visible
    $new_case_control.css("display", "block");
    // Set the value of the checkbox in the case_control
    $('#' + case_name_no_spaces + ' ' + '.case_visibility_checkbox').attr('value', case_name);
    $('#' + case_name_no_spaces + ' ' + '.case_delete_button').attr('value', case_name);
    $('#' + case_name_no_spaces + ' ' + '.case_info_button').attr('value', case_name);
    // Set label in case control equal to case name.
    $('#' + case_name_no_spaces + ' ' + '.case_label').html(case_name)
}

var update_single_case_selector = function(){
    var cases = get_cases_to_plot_from_ui();
    $('#single_case_result_chosen_case').empty();
    $.each(cases, function (i, case_name) {
        $('#single_case_result_chosen_case').append($('<option>', {
            value: case_name,
            text : case_name
        }));
    });
}


var get_cases_to_plot_from_ui = function(){
  case_controls = $("#case_list .case_visibility_checkbox");
  cases_to_plot = []
  $.each(case_controls, function(index, checkbox){
    if (checkbox.checked == true){
       cases_to_plot.push(checkbox.value)
    }
  })
  return cases_to_plot
}


var on_checkbox_change = function(){
  update_single_case_selector();
  plot_results();
}

var check_that_a_case_can_be_added = function(){
    var retail_tariff_set = $('#retail_tariff_selection_panel .select_tariff').val() != 'None';
    var network_tariff_set = $('#network_tariff_selection_panel .select_tariff').val() != 'None';
    var file_name_set = $('#select').children("option:selected").val() != 'Select one';
    var year_set = $('#select_wholesale_year').val() != 'None';
    var state_set = $('#select_wholesale_state').val() != 'None';

    var are_costs_set = (retail_tariff_set || network_tariff_set || (year_set && state_set));

    var message = ""

    if (!are_costs_set && !file_name_set){
        message = "Please select load profiles and a tariff or wholesale energy costs before attempting to create a case."
    } else if (!file_name_set){
        message = "Please select load profiles before attempting to create a case."
    } else if (!are_costs_set){
        message = "Please select a tariff or wholesale energy costs before attempting to create a case."
    }

    if (message != ""){
        $("#message_dialog").dialog({ modal: true});
        $("#message_dialog p").text(message)
    } else  {
        get_default_case_name();
    }

}