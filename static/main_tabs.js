function displayPanels(evt, panelName) {
  // Declare all variables
  var i, tabcontent, tablinks;

  // Get all elements with class="tablinks" and remove the class "active"
  tablinks = document.getElementsByClassName("main_tab_links");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  // Show the current tab, and add an "active" class to the button that opened the tab
  //$("#" + panelName).insertBefore($('.main_tab_content').first());
  $(".main_tab_content").css('z-index', -1)
  $("#" + panelName).css('z-index', 1)
  evt.currentTarget.className += " active";

}