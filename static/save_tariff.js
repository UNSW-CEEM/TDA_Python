var get_tariff_then_save = function(evt, div_that_got_clicked){
    var tariff_type_tab_id = $(div_that_got_clicked).closest('[id]').attr('id');
    // Get the name of the selected tariff.
    var tariff_name = $('#' + tariff_type_tab_id + ' .select_tariff').val();

    var request_details = {
        'tariff_panel': tariff_type_tab_id,
        'tariff_name': tariff_name
    }

    // Ask for the corresponding json.
    $.ajax({
        url: '/tariff_json',
        data: JSON.stringify(request_details),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        // Call the function to display the selected tariffs info
        success: function(data){save_tariff(data, tariff_type_tab_id);},
        error: function(a,b,c){console.log(b); console.log(c);}
    });
}

var save_tariff = function(current_tariff, tariff_type_tab_id){

    current_tariff['Parameters'] = get_tariff_parameters_from_ui(tariff_type_tab_id);

    current_tariff['Name'] = $('#' + tariff_type_tab_id + ' .save_mod_tariff_name').val();

    // Ask the server what the options should be now.
    $.ajax({
        url: '/save_tariff',
        data: JSON.stringify(current_tariff),
        contentType: 'application/json;',
        type : 'POST',
        async: 'false',
        dataType:"json",
        // Update tariff options so the user can select the new tariff.
        success: function(){get_tariff_options(tariff_type_tab_id);},
        error: function(){console.log("Update tariffs not called")}
        });
}


var get_tariff_parameters_from_ui = function(tariff_type_tab_id){

    // Pull tariff data from GUI and format in the standard used for communicating with the python backend.
    var parameters = {};

    // Get the buttons used to display the parameter tabs.
    var tariff_parameter_tab_buttons = $('#' + tariff_type_tab_id + ' .tab_button_area').children();

    // Look through the buttons, using their value to retrieve the correct set of tables.
    $.each(tariff_parameter_tab_buttons, function(index, button){
        var parameter_name = $(button).attr('value');
        parameters[parameter_name] = get_parameter_tables(parameter_name);
    })

    return parameters

}

var get_parameter_tables = function(parameter){
    // Get a list of all the table for the given parameter.
    var parameter_tables = $('#' + parameter + ' .tariff_table');

    // Create an object to add the table data to as it is collected from the UI.
    tables_data = {};

    $.each(parameter_tables, function(index, table){
        var table_name = $(table).attr('value');
        tables_data[table_name] = get_tariff_table_data(parameter, table_name);
    })

    return tables_data
}

var get_tariff_table_data = function(parameter, table_name){
   // Array for the rows of tariff data to get stored in.
   var rows_arr = []
   // Find the table to get the tariff data out of.
   var rows = $('#' + parameter + ' .' + table_name + ' tbody tr');
   // If the table header includes a column for a delete button then start collecting the data from the second column.
   if($('#' + parameter + ' .' + table_name + " thead tr th")[0].innerHTML == ''){
    var start_col = 1
   } else {
    var start_col = 0
   }
   // Loop through the rows in the table
   $.each(rows, function(index, row){
       // Array to store the row values in.
       var row_arr = []
       // Loop through row values and place them in the array.
       for (var j = start_col, col; col = row.cells[j]; j++) {
         row_arr.push(col.innerText);
       }
       // Added array of row values to the array of rows.
       rows_arr.push(row_arr);
   });
   // Array to store the values of the tariff table header in.
   var header = []
   // Loop through the header adding the values to the array.
   $('#' + parameter + ' .' + table_name + " thead tr th").each(function(){
       // Don't save the column header for the delete row buttons.
       if ($(this).text() != ''){
           header.push($(this).text());
       }
   });

   // Consolidate table data into a single object to return.
   var table_data = {table_header: header, table_rows: rows_arr}
   return table_data
}