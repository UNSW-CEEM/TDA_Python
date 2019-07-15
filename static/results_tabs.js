function displayResults(evt, results_type) {
  // Declare all variables
  var i, tabcontent, tablinks;

  // Get all elements with class="tabcontent" and hide them
  tabcontent = document.getElementsByClassName("results_tab_content");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  // Get all elements with class="tablinks" and remove the class "active"
  tablinks = document.getElementsByClassName("results_tab_links");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  // Show the current tab, and add an "active" class to the button that opened the tab
  document.getElementById(results_type).style.display = "block";
  evt.currentTarget.className += " active";

  if ( $('#dual_variable_result_chart').children().length > 0 ) {
    Plotly.Plots.resize('dual_variable_result_chart');
  }
    if ( $('#single_variable_result_chart').children().length > 0 ) {
    Plotly.Plots.resize('single_variable_result_chart');
 }
   if ( $('#single_case_result_chart').children().length > 0 ) {
    Plotly.Plots.resize('single_case_result_chart');
 }

}