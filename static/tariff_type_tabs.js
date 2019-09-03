function displayTariffType(evt, tariffType) {
  // Declare all variables
  var i, tabcontent, tablinks;

  // Get all elements with class="tablinks" and remove the class "active"
  tablinks = document.getElementsByClassName("tariff_type_links");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  // Show the current tab, and add an "active" class to the button that opened the tab
  //$("#" + tariffType).insertBefore($('.tariff_type_tab_content').first());
  $(".tariff_type_tab_content").css('z-index', -2)
  $("#" + tariffType).css('z-index', 2)
  evt.currentTarget.className += " active";

}