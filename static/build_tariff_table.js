// This script populates the tables in the tariff selection panel.

// This function retrieve the json of a single tariff based on the state of the tariff selector.
var get_tariff = function(tariff_type_panel){
    // Get the name of the selected tariff.
    tariff_name = $('#' + tariff_type_panel + ' .select_tariff').val();

    request_details = {'tariff_panel': tariff_type_panel, 'tariff_name': tariff_name}

    // Ask for the corresponding json.
    $.ajax({
        url: '/tariff_json',
        data: JSON.stringify(request_details),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        // Call the function to display the selected tariffs info
        success: function(data){display_tariff_info(tariff_type_panel, data);},
        error: function(a,b,c){console.log(b); console.log(c);}
    });

  // Hide the save option when a new tariff is displayed.
  var tariff_save_option = $('#' + tariff_type_panel + " .save_mod_tariff_option");
  //$(tariff_save_option).css('display', "none")

}

var display_tariff_info = function(tariff_type_panel, tariff_data){
    // display high level info
    $('#' + tariff_type_panel + ' .name_value').html(tariff_data['Name']);
    $('#' + tariff_type_panel + ' .type_value').html(tariff_data['Type']);
    $('#' + tariff_type_panel + ' .state_value').html(tariff_data['State']);

    // display info by nuos, duos etc
    for (var key in tariff_data['Parameters']) {
        if (tariff_data['Parameters'].hasOwnProperty(key)) {
            display_tables(tariff_type_panel, key, tariff_data['Parameters'][key], true);
        }
    }
}

var display_tables = function(tariff_type_panel, parameter_type, data_of_tables, editable){
    // Get a list of the tables currently on display
    var current_tables = $('#' + parameter_type + ' .tariff_table')
    // Tear down all the current tables.
    $.each(current_tables, function(index, table){
        tear_down_current_table(table, true)
    })
    // Delete remaining html
    $('#' + parameter_type).empty();


    // Display the new tables.
    $.each(data_of_tables, function(table_name, table_data){
        // Get a copy of the table template
        var $table_template = $('.tariff_table').first().clone();

        // Add table name to class of table just created.
        $table_template.addClass(table_name)

        // Insert table title
        $("<h4>" + table_name + ":</h4>").appendTo($("#" + parameter_type))
        // Insert table template
        $table_template.appendTo($("#" + parameter_type))

        // Make visible
        $table_template.css("display", "block");

        // Put contents in table.
        display_table_data(parameter_type, table_name, table_data, editable, tariff_type_panel);
    })
}

var tear_down_current_table = function(table, editable){
    // If the html table has already been made into a DataTable, then destroy the DataTable before
    // updating the display.
    if ($.fn.dataTable.isDataTable(table) ) {
        // Get the DataTable instance
        var data_table = $(table).DataTable();
        // If the table was editable destroy this functionality first.
        if (editable){
            data_table.MakeCellsEditable("destroy");
        }
        // Then destroy the DataTable.
        data_table.destroy();
    }

}

var display_table_data = function(parameter_type, table_name, table_data, editable, tariff_type_panel){
    var table_identifier = '#' + parameter_type + ' .' + table_name + '.tariff_table'

    // Set value of table equal to table name, this is used when user edits and saves the table.
    $(table_identifier).attr('value', table_name);

    // Build the table header.
    build_header(table_identifier, table_data['table_header']);

    // Build each row in the table.
    for (var key in table_data['table_rows']){
        if (table_data['table_rows'].hasOwnProperty(key)) {
            build_row(table_data['table_rows'][key], table_identifier)
        }
    }

    // Convert to a DataTable to get scrolling functionality, turn other functionality off.
    table = $(table_identifier).DataTable( {
        //"scrollX": true,
        "paging": false,
        "info": false,
        "searching": false,
        "filter": false,
        "retrieve": true,
        "sort": false
    } );

    // If turned on add editing functionality.
    if (editable){
        panel_specific_call_back = function(){display_save_mod_tariff_option(tariff_type_panel)};
        table.MakeCellsEditable({"onUpdate": panel_specific_call_back});
    }


}

var build_header = function(table_identifier, header_data){
    var length_row = header_data.length
    var tr = document.createElement('tr');
    for (var i = 0; i < length_row; i++){
        var th = document.createElement('th');
        var text = document.createTextNode(header_data[i]);
        th.appendChild(text);
        tr.appendChild(th);
    }
    var header = $(table_identifier + ' .tariff_table_header');
    header.append(tr);
}

var build_row = function(row_data, table_identifier){
    var length_row = row_data.length
    var tr = document.createElement('tr');
    for (var i = 0; i < length_row; i++){
        var td = document.createElement('td');
        var text = document.createTextNode(row_data[i]);
        td.appendChild(text);
        tr.appendChild(td);
    }
    var tariff_table = $(table_identifier + " .tariff_table_body");
    tariff_table.append(tr);
}

var display_save_mod_tariff_option = function(tariff_type_panel) {
  var tariff_save_option = $('#' + tariff_type_panel + " .save_mod_tariff_option");
  //$(tariff_save_option).css('display', "inline")
  var save_name_input = document.getElementById("save_mod_tariff_name");
  var current_name = $('#' + tariff_type_panel + " .name_value").html();
  $('#' + tariff_type_panel + " .save_mod_tariff_name").val(current_name + " v2");
}

