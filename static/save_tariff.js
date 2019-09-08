var get_tariff_then_save = function(tariff_type_tab_id){

    // Get the name of the selected tariff.
    var tariff_name = $('#' + tariff_type_tab_id + ' .select_tariff').val();

    var request_details = {
        'tariff_panel': tariff_type_tab_id,
        'tariff_name': tariff_name
    }

    if (tariff_name !== 'None'){
        // Ask for the corresponding json.
        $.ajax({
            url: '/tariff_json',
            data: JSON.stringify(request_details),
            contentType: 'application/json;charset=UTF-8',
            type : 'POST',
            async: 'false',
            dataType:"json",
            // Call the function to display the selected tariffs info
            success: function(data){
                alert_user_if_error(data);
                get_tariff_details_from_user(data, tariff_type_tab_id);
            }
        });
    } else {
      get_tariff_details_from_user({}, tariff_type_tab_id);
    }

}

var get_tariff_details_from_user = function(current_tariff, tariff_type_tab_id){
    var selected_tariff_name = $('#' + tariff_type_tab_id + ' .select_tariff').val();

    if (selected_tariff_name !== 'None'){
       // Fill default values in meta details editor
       $('#tariff_meta_details_editor .name').prop('value', selected_tariff_name + ' v2')
       $('#tariff_meta_details_editor .provider').prop('value', current_tariff['Provider'])
       $('#tariff_meta_details_editor .type').prop('value', current_tariff['Type'])
       $('#tariff_meta_details_editor .state').prop('value', current_tariff['State'])
       $('#tariff_meta_details_editor .year').prop('value', current_tariff['Year'])
       $('#tariff_meta_details_editor .info').prop('value', current_tariff['Info'])
    } else {
       // Fill default values in meta details editor
       $('#tariff_meta_details_editor .name').prop('value', '')
       $('#tariff_meta_details_editor .provider').prop('value', '')
       $('#tariff_meta_details_editor .type').prop('value', '')
       $('#tariff_meta_details_editor .state').prop('value', '')
       $('#tariff_meta_details_editor .year').prop('value', '')
       $('#tariff_meta_details_editor .info').prop('value', '')
    }

    current_tariff['Parameters'] = get_tariff_parameters_from_ui(tariff_type_tab_id);

    $( "#tariff_meta_details_editor" ).dialog({
        modal: true,
        width: 500,
        buttons: {"Save": function(){
                                     if ($('#tariff_meta_details_editor .name').prop('value') != ''){
                                        save_tariff(current_tariff, tariff_type_tab_id);
                                     } else {
                                        message = "Please provide a name for the tariff."
                                        $("#message_dialog").dialog({ modal: true});
                                        $("#message_dialog p").text(message)
                                     }
                            },
                  "Cancel": function(){$('#tariff_meta_details_editor').dialog('close');}}
    });
}

var save_tariff = function(current_tariff, tariff_type_tab_id){

    // Fill default values in meta details editor
    current_tariff['Name'] = $('#tariff_meta_details_editor .name').prop('value')
    current_tariff['Provider'] = $('#tariff_meta_details_editor .provider').prop('value')
    current_tariff['Type'] = $('#tariff_meta_details_editor .type').prop('value')
    current_tariff['State'] = $('#tariff_meta_details_editor .state').prop('value')
    current_tariff['Year'] = $('#tariff_meta_details_editor .year').prop('value')
    current_tariff['Info'] = $('#tariff_meta_details_editor .info').prop('value')

    if (tariff_type_tab_id == 'network_tariff_selection_panel'){
        current_tariff['ProviderType'] = 'Network'
    } else {
        current_tariff['ProviderType'] = 'Retailer'
    }

    // Ask the server what the options should be now.
    $.ajax({
        url: '/save_tariff',
        data: JSON.stringify(current_tariff),
        contentType: 'application/json;',
        type : 'POST',
        async: 'false',
        dataType:"json",
        // Update tariff options so the user can select the new tariff.
        success: function(data){
            alert_user_if_error(data);
            set_save_button_to_normal_state(tariff_type_tab_id);
            get_tariff_options(tariff_type_tab_id, current_tariff['Name']);
        }
        });

    $('#tariff_meta_details_editor').dialog('close');
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

var check_there_are_parameters_to_save = function(div_that_got_clicked){
    var tariff_type_tab_id = $(div_that_got_clicked).closest('[id]').attr('id');

    if (tariff_type_tab_id == 'network_tariff_selection_panel'){
        component_tab_to_check = '#NUOS'
    } else {
        component_tab_to_check = '#Retail'
    }

    if($(component_tab_to_check).is(':empty')){
        message = "Please add at least one component to the tariff before attempting to save."
        $("#message_dialog").dialog({ modal: true});
        $("#message_dialog p").text(message)
    } else (
        get_tariff_then_save(tariff_type_tab_id)
    )
}

var set_save_button_to_normal_state = function(tariff_type_tab_id){
    $('#' + tariff_type_tab_id + ' .save_mod_button').css('color', 'black');
}
