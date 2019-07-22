
var get_default_case_name = function(){
    // Get a un used case name to put as the default name in the case namer dialog box.
    $.ajax({
        url: '/get_case_default_name',
        contentType: 'application/json;charset=UTF-8',
        async: 'false',
        dataType:"json",
        success: function(data){launch_case_namer(data)}
    });
}


var launch_case_namer = function(default_name){
    $('#case_name').val(default_name)
    $( "#case_namer" ).dialog({
        modal: true,
        buttons: {"Save case": add_case_to_gui}
    });
}

var add_case_to_gui = function(){
    // Get case name
    case_name = $('#case_name').val();
    case_name_no_spaces = case_name.replace(/\s/g, '');

    // Get a copy of the case control template.
    var $new_case_control = $('#case_control_template').clone();
    // Set the id of the copy equal to the case name.
    $new_case_control.attr('id', case_name_no_spaces);
    // Insert the copy into the case panel
    $new_case_control.insertAfter($('#case_list').children().last())
    // Make the case control visible
    $new_case_control.css("display", "block");
    // Set the value of the checkbox in the case_control
    $('#' + case_name_no_spaces + ' ' + '.case_visibility_checkbox').attr('value', case_name);
    $('#' + case_name_no_spaces + ' ' + '.case_delete_button').attr('value', case_name);
    $('#' + case_name_no_spaces + ' ' + '.case_info_button').attr('value', case_name);
    // Set label in case control equal to case name.
    $('#' + case_name_no_spaces + ' ' + '.case_label').html(case_name)
    // Add the case to the python side.
    add_case();
    //Update the select for the single case results.
    update_single_case_selector();
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

var get_active_component = function(){
    var component
    var tablinks = $(".tablinks");
    $.each(tablinks, function(index, link){
        if ($(link).hasClass('active')){
          component = link.value
        }
        return component
    });
    return component
}


var add_case = function(){
    // Get the active component tab when the add case button was clicked.
    var component = get_active_component();

    // Get the name of the selected tariff.
    case_name = $('#case_name').val();

    // Get the name of the selected tariff.
    tariff_name = $('#select_tariff').val();

    // Get load details
    load_request = get_load_details_from_ui();

    // Bundle case details into a single object
    case_details = {'case_name': case_name,
                    'tariff_name': tariff_name,
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

var plot_results = function(){
    // Plot results for each results tab.
    plot_single_variable_results();
    plot_dual_variable_results();
    plot_single_case_results();
    $('#dialog').dialog('close');
    // Always show single variable graph by default.
    document.getElementById('results_panel_button').click();
}

var plot_single_variable_results = function(){
    // Get cases to plot
    cases_to_plot = get_cases_to_plot_from_ui();

    // Get the chart type to be drawn from the GUI.
    var chart_type = $('#single_variable_chart_type').children("option:selected").val();

    // Package request details into a single object.
    var case_details = {'chart_name': chart_type, 'case_names': cases_to_plot}

    // Define the chart layout
    var layout = {margin: { l: 40, r: 35, b: 40, t: 20, pad: 0 },
                  paper_bgcolor: '#EEEEEE',
                  plot_bgcolor: '#c7c7c7',
                  showlegend: true};

    // Get chart data
    $.ajax({
        url: '/get_single_variable_chart',
        data: JSON.stringify(case_details),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            // Draw chart.
            Plotly.newPlot('single_variable_result_chart', data, layout, {responsive: true});
        ;}
    });

}


var plot_dual_variable_results = function(){
    // Get cases to plot
    cases_to_plot = get_cases_to_plot_from_ui();

    // Get the x and y axis for the dual variable chart.
    var x_axis = $('#dual_variable_x_axis').children("option:selected").val();
    var y_axis = $('#dual_variable_y_axis').children("option:selected").val();

    // Package request details into a single object.
    var case_details = {'x_axis': x_axis, 'y_axis': y_axis, 'case_names': cases_to_plot}

    // Define the chart layout
    var layout = {margin: { l: 40, r: 35, b: 40, t: 20, pad: 0 },
                  paper_bgcolor: '#EEEEEE',
                  plot_bgcolor: '#c7c7c7',
                  showlegend: true};

    // Get chart data
    $.ajax({
        url: '/get_dual_variable_chart',
        data: JSON.stringify(case_details),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            // Draw chart.
            Plotly.newPlot('dual_variable_result_chart', data, layout, {responsive: true});
        ;}
    });

}


var plot_single_case_results = function(){
    // Get the name of the case to plot.
    var case_name = $('#single_case_result_chosen_case').children("option:selected").val();

    // Get the x and y axis for the dual variable chart.
    var case_to_plot = $('#single_case_result_chosen_case').children("option:selected").val();
    var chart_type = $('#single_case_chart_type').children("option:selected").val();

    // Package request details into a single object.
    var case_details = {'chart_name': chart_type, 'case_name': case_name}

    // Define the chart layout
    var layout = {margin: { l: 40, r: 35, b: 40, t: 20, pad: 0 },
                  paper_bgcolor: '#EEEEEE',
                  plot_bgcolor: '#c7c7c7',
                  showlegend: true};

    // Get chart data
    $.ajax({
        url: '/get_single_case_chart',
        data: JSON.stringify(case_details),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            // Draw chart.
            Plotly.newPlot('single_case_result_chart', data, layout, {responsive: true});
        ;}
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