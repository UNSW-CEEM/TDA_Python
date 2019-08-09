// This script populates the tables in the tariff selection panel.

// This function retrieve the json of a single tariff based on the state of the tariff selector.
var get_tariff = function(tariff_type_panel){
    // Get the name of the selected tariff.
    tariff_name = $('#' + tariff_type_panel + ' .select_tariff').val();

    if (tariff_name != "None"){
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
        $('#' + tariff_type_panel + ' .component_adder').show();
    } else {
       reset_tariff_options(tariff_type_panel);
       tear_down_tables_in_tariff_type_panel(tariff_type_panel);
       $('#' + tariff_type_panel + ' .component_adder').hide();
    }
}

var tear_down_tables_in_tariff_type_panel = function(parent_id){
    var current_tables = $('#' + parent_id + ' .tariff_table')
    // Tear down all the current tables.
    $.each(current_tables, function(index, table){
        tear_down_current_table(table, true)
    })

    var table_sets = $('#' + parent_id + ' .table_set')
    // Tear down all the current tables.
    $.each(table_sets, function(index, set){
       $(set).empty();
    })
}

var display_tariff_info = function(tariff_type_panel, tariff_data){
    // Hide tariff creation features.
    disable_tariff_creation();

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

var display_tables = function(tariff_type_panel, parameter_type, data_of_tables, editable, clear=true){

    // If clear set to true then delete current tables
    if(clear){
        // Get a list of the tables currently on display
        var current_tables = $('#' + parameter_type + ' .tariff_table')
        // Tear down all the current tables.
        $.each(current_tables, function(index, table){
            tear_down_current_table(table, true)
        })
        // Delete remaining html
        $('#' + parameter_type).empty();
    }


    // Display the new tables.
    $.each(data_of_tables, function(table_name, table_data){
        // Only add table if one with the same name does not already exist.
        if($('#' + parameter_type + ' .tariff_table[value={}]'.replace('{}', table_name)).length < 1){
            // Get a copy of the table template
            var $table_template = $('.tariff_table').first().clone();

            // Add table name to class of table just created.
            $table_template.addClass(table_name)

            // Insert table title
            $("<h4 class='" + table_name  + "'>" + table_name + ":</h4>").appendTo($("#" + parameter_type))
            // Insert table template
            $table_template.appendTo($("#" + parameter_type))

            // Make visible
            $table_template.css("display", "block");

            // Decide if the table is multi row, used to determine if the user can delete and add rows.
            var multi_row = table_data['table_header'].includes("Name")

            // Put contents in table.
            display_table_data(parameter_type, table_name, table_data, editable, multi_row, tariff_type_panel);

            // Insert a button for adding a row to the table
            if (editable){
                if (multi_row){
                    $("<div class='{c}' style='width: 100%; height: 15%'><button onclick=\"user_add_row('{a}', '{b}', '{c}')\">&#10010;</button><button onclick=\"user_delete_table('{a}', '{c}')\">&#10006</button></div>"
                    .replace(/{a}/g, tariff_type_panel).replace(/{b}/g, parameter_type).replace(/{c}/g, table_name)).appendTo($("#" + parameter_type))
                } else {
                    $("<div class='{b}' style='width: 100%; height: 15%'><button onclick=\"user_delete_table('{a}', '{b}')\">&#10006</button></div>"
                    .replace(/{a}/g, tariff_type_panel).replace(/{b}/g, table_name)).appendTo($("#" + parameter_type))
                }
            } else {
                // Spacer to keep layout consistent even if there is no button.
                $("<div class='{}' style='width: 100%; height: 10%'></div>".replace(/{}/g, table_name)).appendTo($("#" + parameter_type))
            }

        }
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

var display_table_data = function(parameter_type, table_name, table_data, editable, multi_row, tariff_type_panel){
    var table_identifier = '#' + parameter_type + ' .' + table_name + '.tariff_table'

    // Set value of table equal to table name, this is used when user edits and saves the table.
    $(table_identifier).attr('value', table_name);

    // Build the table header.
    build_header(table_identifier, table_data['table_header'], editable, multi_row);

    // Build each row in the table.
    for (var key in table_data['table_rows']){
        if (table_data['table_rows'].hasOwnProperty(key)) {
            build_row(table_data['table_rows'][key], table_identifier, editable, multi_row, tariff_type_panel)
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
        table.MakeCellsEditable({"onUpdate": update_table_structures_after_edit,
                                 "columns": columns_to_edit(table_data, multi_row)});
    }
}



var update_table_structures_after_edit = function(updatedCell, updatedRow, oldValue){
    var edited_table_id = updatedRow.table().node().id
    var edited_table = $('#' + edited_table_id)
    var tariff_type_panel = $(edited_table).closest('.tariff_type_tab_content').attr('id');
    var table_name = $(edited_table).attr('value');
    var tables = $('#' + tariff_type_panel + ' .tariff_table.' + table_name)
    var row_index = updatedCell.index()['row']
    var column_index = updatedCell.index()['column']
    if ($(edited_table).DataTable().column(column_index).header().innerHTML !== 'Value'){
        $.each(tables, function(i, table){
            $(table).DataTable().cell(row_index, column_index).data(updatedCell.data());
        });
    }
}

var build_header = function(table_identifier, header_data, editable, multi_row){
    var length_row = header_data.length
    var tr = document.createElement('tr');
    // If the table is editable and has a Name column (i.e. is has multiple rows), then add a column in the header
    // that matches the column with the row delete buttons, leave the name blank.
    if (editable & multi_row){
        var th = document.createElement('th');
        var text = document.createTextNode('');
        th.appendChild(text);
        tr.appendChild(th);
    }
    for (var i = 0; i < length_row; i++){
        var th = document.createElement('th');
        var text = document.createTextNode(header_data[i]);
        th.appendChild(text);
        tr.appendChild(th);
    }
    var header = $(table_identifier + ' .tariff_table_header');
    header.append(tr);
}

var build_row = function(row_data, table_identifier, editable, multi_row, tariff_type_panel){
    var length_row = row_data.length
    var tr = document.createElement('tr');
    // If the table is editable and has a Name column (i.e. is has multiple rows), then add a button for deleting
    // rows.
    if (editable & multi_row){
        var td = document.createElement('td');
        var delete_button = document.createElement('template');
        delete_button.innerHTML = "<button onclick=\"user_delete_row(this, '{}')\">&#10006</button>".
            replace('{}', tariff_type_panel)
        td.appendChild(delete_button.content.firstChild);
        tr.appendChild(td);
    }
    for (var i = 0; i < length_row; i++){
        var td = document.createElement('td');
        var text = document.createTextNode(row_data[i]);
        td.appendChild(text);
        tr.appendChild(td);
    }
    var tariff_table = $(table_identifier + " .tariff_table_body");
    tariff_table.append(tr);
}

var user_add_row = function(tariff_type_panel, parameter_type, table_name){
    var rows =  $('#' + parameter_type + ' .tariff_table.' + table_name).DataTable().rows().data();
    var last_row =  rows[rows.length - 1];
    var tables = $('#' + tariff_type_panel + ' .tariff_table.' + table_name)
    $.each(tables, function(i, table){
        $(table).DataTable().row.add(last_row).draw();
    });
}

var user_delete_row = function(row, tariff_type_panel){
    var table = $(row).closest('.tariff_table');
    var table_name = $(table).attr('value');
    var row_index = $(row).parents('tr').index();
    var tables_to_edit = $('#' + tariff_type_panel + ' .tariff_table.' + table_name)
    $.each(tables_to_edit, function(i, table_to_edit){
        $(table_to_edit).DataTable().row(row_index).remove().draw();
    });
    //table.DataTable().row($(row).parents('tr')).remove().draw();
}

var user_delete_table = function(tariff_type_panel, table_name){
    var tables = $('#' + tariff_type_panel + ' .tariff_table.' + table_name)
    $.each(tables, function(i, table){
        tear_down_current_table(table, true);
    });
    $('#' + tariff_type_panel + ' .' + table_name).remove()
}

var columns_to_edit = function(table_data, multi_row){
    var l = table_data['table_rows'][0].length
    var column_indexes = []
    for (var i = 0; i < l; i++){
        if (table_data['table_header'][i] !== 'Unit'){
            if (multi_row){
                column_indexes.push(i + 1)
            } else {
                column_indexes.push(i)
            }

        }
    }
    return column_indexes
}

var nuos_equals_duos_plus_tuos = function(){
    var duos_tables = $('#DUOS .tariff_table')
    var tuos_tables = $('#TUOS .tariff_table')
    var dtuos_tables = $('#DTUOS .tariff_table')
    var nuos_tables = $('#NUOS .tariff_table')

    $.each(duos_tables, function(i, duos_table){
        column_index = get_value_index_in_header($(duos_table).attr('value'))
        number_rows = $(duos_table).DataTable().rows().indexes().length
        for (var j = 0; j < number_rows; j++){
            var duos_value = parseFloat($(duos_tables[i]).DataTable().cell(j, column_index).data());
            var tuos_value = parseFloat($(tuos_tables[i]).DataTable().cell(j, column_index).data());
            var new_value = (duos_value + tuos_value).toFixed(4)
            $(dtuos_tables[i]).DataTable().cell(j, column_index).data(new_value);
            $(nuos_tables[i]).DataTable().cell(j, column_index).data(new_value);
        }
    });
}

var get_value_index_in_header = function(table_name){
    var header_row = $('#DUOS .' + table_name + '.tariff_table thead tr th');
    for (var i = 0; i < header_row.length; i++){
        if(header_row[i].innerHTML == 'Value'){
            var value_index = i
        }
    }
    return value_index
}