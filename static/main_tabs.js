function displayPanels(evt, panelName) {
  // Declare all variables
  var i, tabcontent, tablinks;

  // Get all elements with class="tablinks" and remove the class "active"
  tablinks = document.getElementsByClassName("main_tab_links");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  // Show the current tab, and add an "active" class to the button that opened the tab
  $("#" + panelName).insertBefore($('.main_tab_content').first());
  evt.currentTarget.className += " active";

  if (panelName == 'load_panel'){
    setup_vertical_resizing_pair('#load_selection', '#load_inspection', 'load_chart');
  }

  if (panelName == 'wholesale_energy_costs_selection_panel'){
    //setup_vertical_resizing_pair('#wholesale_price_selection', '#price_inspection', 'price_chart');
  }

}