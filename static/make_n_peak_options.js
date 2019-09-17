// Add the possible number of peaks to the n= drop down menu
for (i = 1; i <= 150; i++) {
  var o = new Option("option text", "value");
  $(o).html(i.toString());
  $("#x_n_peaks_select").append($(o).clone());
  $("#y_n_peaks_select").append($(o).clone());
}

// Update the visibility of the n peaks options.
var control_options_display = function(axis){
    var options = $('.' + axis + "_peak_options");
    var axis_type = $('#dual_variable_' + axis + '_axis').children("option:selected").val();
    if (axis_type == 'avg_demand_n_peaks' || axis_type == 'avg_demand_n_monthly_peaks' || axis_type == 'avg_demand_top_n_peaks' || axis_type == 'avg_demand_top_n_monthly_peaks'){
      options.css('visibility', 'visible');;
    } else {
      options.css('visibility', 'hidden');;
    }
}


// Update the visibility of the n peaks options.
var control_options_block_display = function(){
    var options = $("#peak_options_container");
    var options_season = $("#select_seasons");

    var x_axis = $('#dual_variable_x_axis').children("option:selected").val();
    var y_axis = $('#dual_variable_y_axis').children("option:selected").val();
    if ( x_axis == 'avg_demand_n_peaks'|| y_axis == 'avg_demand_n_peaks' || 
         x_axis == 'avg_demand_n_monthly_peaks'|| y_axis == 'avg_demand_n_monthly_peaks' || 
         x_axis == 'avg_demand_top_n_peaks'|| y_axis == 'avg_demand_top_n_peaks' ||
         x_axis == 'avg_demand_top_n_monthly_peaks'|| y_axis == 'avg_demand_top_n_monthly_peaks'){
      options.show();
      options_season.show();
    } else {
      options.hide();
      options_season.hide();
    }
}


// Run the function that updates the visibility when the user picks a new y axis.
$('#dual_variable_y_axis').on('change', function(){
    control_options_block_display();
    control_options_display('y');
});

// Run the function that updates the visibility when the user picks a new x axis.
$('#dual_variable_x_axis').on('change', function(){
    control_options_block_display();
    control_options_display('x');
});