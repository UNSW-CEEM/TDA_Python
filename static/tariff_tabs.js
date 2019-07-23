function displayTariff(evt, unique_parent_id, tariffName) {
  // Declare all variables
  var i, tabcontent, tablinks;

  // Get all elements with class="tablinks" and remove the class "active"
  tablinks = $('#' + unique_parent_id + " .tablinks");
  $.each(tablinks, function(index, link){
    $(link).removeClass('active');
  });

  // Show the current tab, and add an "active" class to the button that opened the tab
  $("#" + tariffName).insertBefore($('#' + unique_parent_id + ' .tabcontent').first());
  evt.currentTarget.className += " active";

}