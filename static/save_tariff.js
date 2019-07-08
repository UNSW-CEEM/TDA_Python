var get_tariff_data_from_ui = function(){
    var name = "new tariff"
    var label = document.getElementById("type_label");
    var type = label.innerHTML
    var new_tariff = {Name: name, Type: type,
        Parameters: {DUOS: {Daily: {Unit: "$/day", Value: $("#DUOS_daily_charge").val()},
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
    }}
    return new_tariff
}

var get_tariff_table_data = function(table_name){
   var rows_arr = []
   var table = document.getElementById(table_name + "_tariff_table");
   for (var i = 1, row; row = table.rows[i]; i++) {
       //iterate through rows
       //rows would be accessed using the "row" variable assigned in the for loop
       var row_arr = []
       for (var j = 0, col; col = row.cells[j]; j++) {
         //iterate through columns
         //columns would be accessed using the "col" variable assigned in the for loop
         row_arr.push(col.innerText);
       }
       rows_arr.push(row_arr);
   }
    var header = []
    $("#" + table_name + "_tariff_table thead tr th").each(function(){
        header.push($(this).text());
    });
    var table_data = {table_header: header, table_rows: rows_arr}
    return table_data
}