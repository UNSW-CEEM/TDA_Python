
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
    // Get cases to plot
    cases_to_plot = get_cases_to_plot_from_ui();
    // Get the load details
    load_request = get_load_details_from_ui();


    var n_peaks_selected = $('#n_peaks_select').children("option:selected").val();
    var one_peak_per_day = $("#one_peak_per_day").is(':checked');
    var spring_Ckb = $("#spring_check_box").is(':checked');
    var summer_Ckb = $("#summer_check_box").is(':checked');
    var autumn_Ckb = $("#autumn_check_box").is(':checked');
    var winter_Ckb = $("#winter_check_box").is(':checked');

    // Get the x and y axis for the dual variable chart.
    var x_axis = $('#dual_variable_x_axis').children("option:selected").val();
    var y_axis = $('#dual_variable_y_axis').children("option:selected").val();

    // Package request details into a single object.
    var case_details = {'x_axis': x_axis, 'y_axis': y_axis, 'case_names': cases_to_plot, 'load_details': load_request,
                        'n_peaks_selected': n_peaks_selected, 'one_peak_per_day_status': one_peak_per_day,
                        'spring_status': spring_Ckb, 'summer_status': summer_Ckb, 'autumn_status': autumn_Ckb, 'winter_status': winter_Ckb,}

    // Get chart data
    $.ajax({
        url: '/get_dual_variable_chart',
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

            // Draw chart.
            Plotly.newPlot('dual_variable_result_chart', data['data'], layout, {responsive: true});
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
            // Define the chart layout
            var layout = {margin: { l: 40, r: 35, b: 40, t: 20, pad: 0 },
            paper_bgcolor: '#EEEEEE',
            plot_bgcolor: '#c7c7c7',
            showlegend: true,
            xaxis: data['layout'].xaxis,
            yaxis: data['layout'].yaxis};
            // Draw chart.
            Plotly.newPlot('single_case_result_chart', data['data'], layout, {responsive: true});
        ;}
    });
}