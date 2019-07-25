var get_tariff_then_save = function(evt, tariff_type_tab_id){

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

    current_tariff['Parameters'] = get_tariff_parameters_from_ui();

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


var get_tariff_parameters_from_ui = function(){

    // Pull tariff data from GUI and format in the standard used for communicating with the python backend.
    var parameters = {DUOS: get_parameter_tables("DUOS"),
                     TUOS: get_parameter_tables("TUOS"),
                     DTUOS: get_parameter_tables("DTUOS"),
                     NUOS: get_parameter_tables("NUOS")
                     }
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
   // Loop through the rows in the table
   $.each(rows, function(index, row){
       // Array to store the row values in.
       var row_arr = []
       // Loop through row values and place them in the array.
       for (var j = 0, col; col = row.cells[j]; j++) {
         row_arr.push(col.innerText);
       }
       // Added array of row values to the array of rows.
       rows_arr.push(row_arr);
   });
   // Array to store the values of the tariff table header in.
   var header = []
   // Loop through the header adding the values to the array.
   $('#' + parameter + ' .' + table_name + " thead tr th").each(function(){
       header.push($(this).text());
   });

   // Consolidate table data into a single object to return.
   var table_data = {table_header: header, table_rows: rows_arr}
   return table_data
}