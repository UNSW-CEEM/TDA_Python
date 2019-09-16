
var plot_results = function(){
    // Plot results for each results tab.
    plot_single_variable_results('#single_variable_chart_type', 'single_variable_result_chart')
    plot_single_variable_results('#single_variable_chart_type_2', 'single_variable_result_chart_2')
    plot_dual_variable_results();
    plot_single_case_results();
    $('#dialog').dialog('close');
    // Always show single variable graph by default.
    document.getElementById('results_panel_button').click();
}



var plot_single_variable_results = function(chart_type_selector_id, chart_div_id){
    // Get cases to plot
    cases_to_plot = get_cases_to_plot_from_ui();
    console.log('cases_to_plot:',cases_to_plot)

    // Get the chart type to be drawn from the GUI.
    var chart_type = $(chart_type_selector_id).children("option:selected").val();
    console.log('chart_type:',chart_type)

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

            Plotly.newPlot(chart_div_id, data['data'], layout, {responsive: true});
        }
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


$('#single_variable_chart_type').on('change', function() {
    plot_single_variable_results('#single_variable_chart_type', 'single_variable_result_chart');
});

$('#single_variable_chart_type_2').on('change', function() {
    plot_single_variable_results('#single_variable_chart_type_2', 'single_variable_result_chart_2');
});

$('#x_n_peaks_select').on('change', function() {
    plot_dual_variable_results();
});

$('#y_n_peaks_select').on('change', function() {
    plot_dual_variable_results();
});

$('#x_one_peak_a_day').on('change', function() {
    plot_dual_variable_results();
});

$('#y_one_peak_a_day').on('change', function() {
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