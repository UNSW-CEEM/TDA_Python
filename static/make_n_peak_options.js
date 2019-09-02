// Add the possible number of peaks to the n= drop down menu
for (i = 1; i <= 150; i++) {
  var o = new Option("option text", "value");
  $(o).html(i.toString());
  $("#n_peaks_select").append(o);
}

// Update the visibility of the n peaks options.
var control_options_display = function(){
    var options = document.getElementById("peak_options");
    console.log('options:',options)

    var x_axis = $('#dual_variable_x_axis').children("option:selected").val();
    var y_axis = $('#dual_variable_y_axis').children("option:selected").val();
    if ( x_axis == 'avg_demand_n_peaks'|| y_axis == 'avg_demand_n_peaks' || 
         x_axis == 'avg_demand_n_monthly_peaks' || y_axis == 'avg_demand_n_monthly_peaks' || 
         x_axis == 'avg_demand_top_n_peaks'|| y_axis == 'avg_demand_top_n_peaks' || 
         x_axis == 'avg_demand_top_n_monthly_peaks' || y_axis == 'avg_demand_top_n_monthly_peaks'){
      options.style.display = "block";
    } else {
      options.style.display = "none";
    }
}

// Run the function that updates the visibility when the user picks a new y axis.
$('#dual_variable_y_axis').on('change', function(){
    control_options_display();
});

// Run the function that updates the visibility when the user picks a new x axis.
$('#dual_variable_x_axis').on('change', function(){
    control_options_display();
});