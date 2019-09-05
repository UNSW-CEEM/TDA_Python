// Add the possible number of peaks to the n= drop down menu
for (i = 1; i <= 150; i++) {
  var o = new Option("option text", i);
  $(o).html(i.toString());
  $("#x_n_peaks_select").append($(o).clone());
  $("#y_n_peaks_select").append($(o).clone());
}


// Update the visibility of the n peaks options.
var control_options_block_display = function(){
    var options = $("#peak_options_container");
    var x_axis = $('#dual_variable_x_axis').children("option:selected").val();
    var y_axis = $('#dual_variable_y_axis').children("option:selected").val();
    if ( x_axis == 'avg_demand_n_peaks'|| y_axis == 'avg_demand_n_peaks' || 
    x_axis == 'avg_demand_n_monthly_peaks' || y_axis == 'avg_demand_n_monthly_peaks' || 
    x_axis == 'avg_demand_top_n_peaks'|| y_axis == 'avg_demand_top_n_peaks' || 
    x_axis == 'avg_demand_top_n_monthly_peaks' || y_axis == 'avg_demand_top_n_monthly_peaks'){
      options.show();
    } else {
      options.hide();
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