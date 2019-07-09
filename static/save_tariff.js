var get_tariff_then_save = function(){
    // Get the name of the selected tariff.
    tariff_name = $('#select_tariff').val();

    // Ask for the corresponding json.
    $.ajax({
        url: '/tariff_json',
        data: JSON.stringify(tariff_name),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        // Call the function to display the selected tariffs info
        success: function(data){save_tariff(data);},
        error: function(a,b,c){console.log(b); console.log(c);}
    });
}

var save_tariff = function(current_tariff){
    var name = document.getElementById("save_mod_tariff_name").value

    tariff_parameters = get_tariff_parameters_from_ui()

    current_tariff['Parameters'] = tariff_parameters

    current_tariff['Name'] = name

    // Ask the server what the options should be now.
    $.ajax({
        url: '/save_tariff',
        data: JSON.stringify(current_tariff),
        contentType: 'application/json;',
        type : 'POST',
        async: 'false',
        dataType:"json"
        });
}


var get_tariff_parameters_from_ui = function(){

    // Pull tariff data from GUI and format in the standard used for communicating with the python backend.
    var parameters = {DUOS: {Daily: {Unit: "$/day", Value: $("#DUOS_daily_charge").val()},
                            Energy: {Unit: "$/kWh", Value: $("#DUOS_energy_charge").val()},
                            table_data: get_tariff_table_data("DUOS")},
                     TUOS: {Daily: {Unit: "$/day", Value: $("#TUOS_daily_charge").val()},
                            Energy: {Unit: "$/kWh", Value: $("#TUOS_energy_charge").val()},
                            table_data: get_tariff_table_data("TUOS")},
                     DTUOS: {Daily: {Unit: "$/day", Value: $("#DTUOS_daily_charge").val()},
                            Energy: {Unit: "$/kWh", Value: $("#DTUOS_energy_charge").val()},
                            table_data: get_tariff_table_data("DTUOS")},
                     NUOS: {Daily: {Unit: "$/day", Value: $("#NUOS_daily_charge").val()},
                            Energy: {Unit: "$/kWh", Value: $("#NUOS_energy_charge").val()},
                            table_data: get_tariff_table_data("NUOS")}
                    }
    return parameters
}

var get_tariff_table_data = function(table_name){
   // Array for the rows of tariff data to get stored in.
   var rows_arr = []
   // Find the table to get the tariff data out of.
   var table = document.getElementById(table_name + "_tariff_table");
   // Loop through the rows in the table
   for (var i = 1, row; row = table.rows[i]; i++) {
       // Array to store the row values in.
       var row_arr = []
       // Loop through row values and place them in the array.
       for (var j = 0, col; col = row.cells[j]; j++) {
         row_arr.push(col.innerText);
       }
       // Added array of row values to the array of rows.
       rows_arr.push(row_arr);
   }

   // Array to store the values of the tariff table header in.
   var header = []
   // Loop through the header adding the values to the array.
   $("#" + table_name + "_tariff_table thead tr th").each(function(){
       header.push($(this).text());
   });

   // Consolidate table data into a single object to return.
   var table_data = {table_header: header, table_rows: rows_arr}
   return table_data
}