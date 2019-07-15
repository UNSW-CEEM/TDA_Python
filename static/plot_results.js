
var add_case = function(){
    // Get the name of the selected tariff.
    tariff_name = $('#select_tariff').val();

    // Get load details
    load_request = get_load_details_from_ui();

    // Bundle case details into a single object
    case_details = {'case_name': "dummy_case",
                    'tariff_name': tariff_name,
                    'load_details': load_request};

    // Get the python app to create the case and calculate results, after this is done create the result plots.
    $.ajax({
        url: '/add_case',
        data: JSON.stringify(case_details),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){plot_results()}
    });

}

var plot_results = function(){
    // Plot results for each results tab.
    plot_single_variable_results();
    plot_dual_variable_results();
    plot_single_case_results();
    // Always show single variable graph by default.
    document.getElementById('default_results_tab').click();
}

var plot_single_variable_results = function(){

    // Get the chart type to be drawn from the GUI.
    var chart_type = $('#single_variable_chart_type').children("option:selected").val();

    // Package request details into a single object.
    var case_details = {'chart_name': chart_type, 'case_name': 'dummy_case'}

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
            // Make sure chart area is visible before drawing charts, this makes sure sizing will be done correctly.
            document.getElementById('results_panel_button').click();
            document.getElementById('default_results_tab').click();
            // Draw chart.
            Plotly.newPlot('single_variable_result_chart', data, layout, {responsive: true});
        ;}
    });

}


var plot_dual_variable_results = function(){

    // Get the x and y axis for the dual variable chart.
    var x_axis = $('#dual_variable_x_axis').children("option:selected").val();
    var y_axis = $('#dual_variable_y_axis').children("option:selected").val();

    // Package request details into a single object.
    var case_details = {'x_axis': x_axis, 'y_axis': y_axis, 'case_name': 'dummy_case'}

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
            // Make sure chart area is visible before drawing charts, this makes sure sizing will be done correctly.
            document.getElementById('results_panel_button').click();
            document.getElementById('dual_var_button').click();
            // Draw chart.
            Plotly.newPlot('dual_variable_result_chart', data, layout, {responsive: true});
        ;}
    });

}


var plot_single_case_results = function(){

    // Get the x and y axis for the dual variable chart.
    var case_to_plot = $('#single_case_result_chosen_case').children("option:selected").val();
    var chart_type = $('#single_case_chart_type').children("option:selected").val();

    // Package request details into a single object.
    var case_details = {'chart_name': chart_type, 'case_name': case_to_plot}

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
            // Make sure chart area is visible before drawing charts, this makes sure sizing will be done correctly.
            document.getElementById('results_panel_button').click();
            document.getElementById('single_case_button').click();
            // Draw chart.
            Plotly.newPlot('single_case_result_chart', data, layout, {responsive: true});
        ;}
    });

}