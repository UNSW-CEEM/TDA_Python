
var get_default_case_name = function(event, div_that_got_clicked){
    var parent_id = $(div_that_got_clicked).closest('[id]').attr('id');
    console.log(parent_id)
    // Get a un used case name to put as the default name in the case namer dialog box.
    $.ajax({
        url: '/get_case_default_name',
        contentType: 'application/json;charset=UTF-8',
        async: 'false',
        dataType:"json",
        success: function(data){launch_case_namer(data, parent_id)}
    });
}


var launch_case_namer = function(default_name, parent_id){
    $('#case_name').val(default_name)
    $( "#case_namer" ).dialog({
        modal: true,
        buttons: {"Save case": function(){add_case(parent_id)}}
    });
}

var add_case = function(parent_id){
    case_name = $('#case_name').val();
    add_case_to_gui(case_name)
    add_case_to_python(parent_id);
    update_single_case_selector();
}

var add_case_to_gui = function(case_name){
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
  //update_single_case_selector();
  cases_to_plot = get_cases_to_plot_from_ui();
  plot_results();
}



$('#single_variable_chart_type').on('change', function() {
    plot_results();
});

$('#dual_variable_x_axis').on('change', function() {
    plot_results();
});

$('#dual_variable_y_axis').on('change', function() {
    plot_results();
});

$('#single_case_chart_type').on('change', function() {
    plot_results();
});

$('#n_peaks_select').on('change',function() {
    plot_results();
});

$('#spring_check_box').on('change',function(){
    plot_results();
})

$('#summer_check_box').on('change',function(){
    plot_results();
})
$('#autumn_check_box').on('change',function(){
    plot_results();
})
$('#winter_check_box').on('change',function(){
    plot_results();
})
$('#one_peak_per_day').on('change',function(){
    plot_results();
})




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
    console.log('cases_to_plot:',cases_to_plot)

    // Get the chart type to be drawn from the GUI.
    var chart_type = $('#single_variable_chart_type').children("option:selected").val();

    // Package request details into a single object.
    var case_details = {'chart_name': chart_type, 'case_names': cases_to_plot}


    // Get chart data
    $.ajax({
        url: '/get_single_variable_chart',
        data: JSON.stringify(case_details),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            alert_user_if_error(data)
            // Draw chart.
             // Define the chart layout
            var layout = {margin: { l: 40, r: 35, b: 40, t: 20, pad: 0 },
                            paper_bgcolor: '#EEEEEE',
                            plot_bgcolor: '#c7c7c7',
                            showlegend: data['layout'].showlegend,
                            xaxis: data['layout'].xaxis,
                            yaxis: data['layout'].yaxis};

            Plotly.newPlot('single_variable_result_chart', data['data'], layout, {responsive: true});
        ;}
    });

}

var plot_dual_variable_results = function(){
    var case_details = {}

    // Get the load details
    case_details['load_details'] = get_load_details_from_ui();

    // Get cases to plot
    case_details['case_names'] = get_cases_to_plot_from_ui();

    // Get the x and y axis for the dual variable chart.
    case_details['x_axis'] = $('#dual_variable_x_axis').children("option:selected").val();
    case_details['y_axis'] = $('#dual_variable_y_axis').children("option:selected").val();

    // Get the season to include
    case_details['include_spring'] = $('#include_spring').is(":checked");
    case_details['include_autumn'] = $('#include_autumn').is(":checked");
    case_details['include_winter'] = $('#include_winter').is(":checked");
    case_details['include_summer'] = $('#include_summer').is(":checked");

    // Get peak options
    case_details['x_axis_n_peaks'] = $('#x_n_peaks_select').children("option:selected").text();
    case_details['y_axis_n_peaks'] = $('#y_n_peaks_select').children("option:selected").text();
    case_details['x_axis_one_peak_per_day'] = $('#x_one_peak_a_day').is(":checked");
    case_details['y_axis_one_peak_per_day'] = $('#y_one_peak_a_day').is(":checked");

    // Get chart data
    $.ajax({
        url: '/get_dual_variable_chart',
        data: JSON.stringify(case_details),
        contentType: 'application/json',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){

            // Define the chart layout
            var layout = {margin: { l: 40, r: 35, b: 40, t: 20, pad: 0 },
            paper_bgcolor: '#EEEEEE',
            plot_bgcolor: '#c7c7c7',
            showlegend: true,
            xaxis: data['layout'].xaxis,
            yaxis: data['layout'].yaxis};

            alert_user_if_error(data)

            // Draw chart.
            Plotly.newPlot('dual_variable_result_chart', data['data'], layout, {responsive: true});
        }
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
            // Define the chart layout
            var layout = {margin: { l: 40, r: 35, b: 40, t: 20, pad: 0 },
            paper_bgcolor: '#EEEEEE',
            plot_bgcolor: '#c7c7c7',
            showlegend: true,
            xaxis: data['layout'].xaxis,
            yaxis: data['layout'].yaxis};

            alert_user_if_error(data)
            // Draw chart.
            Plotly.newPlot('single_case_result_chart', data['data'], layout, {responsive: true});
        ;}
    });
}


$('#plot_single_variable_results').on('change', function() {
    plot_single_variable_results();
});

$('.x_peak_options').on('change', function() {
    plot_dual_variable_results();
});

$('#dual_variable_x_axis').on('change', function() {
    plot_dual_variable_results();
});

$('#dual_variable_y_axis').on('change', function() {
    plot_dual_variable_results();
});

$('.season_option').on('change', function() {
    plot_dual_variable_results();
});

$('#single_case_result_chosen_case').on('change', function() {
    plot_single_case_results();
});

$('#single_case_chart_type').on('change', function() {
    plot_single_case_results();
});