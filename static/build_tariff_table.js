// This script populates the tables in the tariff selection panel.

// This function retrieve the json of a single tariff based on the state of the tariff selector.
var get_tariff = function(){
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
        success: function(data){display_tariff_info(data);},
        error: function(a,b,c){console.log(b); console.log(c);}
    });

}

var display_tariff_info = function(tariff_data){
    // display high level info
    var label = document.getElementById("name_value");
    label.innerHTML = tariff_data['Name']
    var label = document.getElementById("type_value");
    label.innerHTML = tariff_data['Type']
    var label = document.getElementById("state_value");
    label.innerHTML = tariff_data['State']

    // display info by nuos, duos etc
    for (var key in tariff_data['Parameters']) {
        if (tariff_data['Parameters'].hasOwnProperty(key)) {
            display_charge_data(key, tariff_data['Parameters'][key]);
            display_table_data(key, tariff_data['Parameters'][key]);
        }
    }
}

var display_charge_data = function(table_name, tariff_data){
    document.getElementById(table_name + "_daily_charge").value = tariff_data['Daily']['Value'];
    if ('Energy' in tariff_data){
        document.getElementById(table_name + "_energy_charge").value = tariff_data['Daily']['Value'];
    }
}

var tear_down_current_table = function(table_name, editable){
    // If the html table has already been made into a DataTable, then destroy the DataTable before
    // updating the display.
    if ($.fn.dataTable.isDataTable( '#' + table_name + '_tariff_table' ) ) {
        // Get the DataTable instance
        var table = $('#' + table_name + '_tariff_table').DataTable();
        // If the table was editable destroy this functionality first.
        if (editable){
            table.MakeCellsEditable("destroy");
        }
        // Then destroy the DataTable.
        $('#' + table_name + '_tariff_table').DataTable().destroy();
    }

    // Remove any existing table rows.
    $('#' + table_name + '_tariff_table' + ' tr').remove();
}

var display_table_data = function(table_name, tariff_data, editable){
    tear_down_current_table(table_name, editable)

    // If the new data set has table data proceed to build the new table.
    if ('table_data' in tariff_data){

        // Build the table header.
        build_header(table_name, tariff_data['table_data']['table_header'])

        // Build each row in the table.
        for (var key in tariff_data['table_data']['table_rows']){
            if (tariff_data['table_data']['table_rows'].hasOwnProperty(key)) {
                build_row(tariff_data['table_data']['table_rows'][key], table_name + '_tariff_table')
            }
        }

        // Convert to a DataTable to get scrolling functionality, turn other functionality off.
        table = $('#' + table_name + '_tariff_table').DataTable( {
            "scrollY": '25vh',
            "scrollX": true,
            "paging": false,
            "info": false,
            "searching": false,
            "filter": false,
            "retrieve": true
        } );

        // If turned on add editing functionality.
        if (editable){
            table.MakeCellsEditable({"onUpdate": display_save_mod_tariff_option});
        }
    }
}

var build_header = function(table_name, header_data){
    var length_row = header_data.length
    var tr = document.createElement('tr');
    for (var i = 0; i < length_row; i++){
        var th = document.createElement('th');
        var text = document.createTextNode(header_data[i]);
        th.appendChild(text);
        tr.appendChild(th);
    }
    var header = document.getElementById( table_name + '_tariff_table_header');
    header.appendChild(tr);
}

var build_row = function(row_data, table_id){
    var length_row = row_data.length
    var tr = document.createElement('tr');
    for (var i = 0; i < length_row; i++){
        var td = document.createElement('td');
        var text = document.createTextNode(row_data[i]);
        td.appendChild(text);
        tr.appendChild(td);
    }
    var tariff_table = document.getElementById(table_id + "_body");
    tariff_table.appendChild(tr);
}

// Get the options every time someone updates a tariff drop down.
$('#select_tariff').on('change', function() {
    console.log('try and load tariff')
    get_tariff();
});

var display_save_mod_tariff_option = function() {
  var tariff_save_option = document.getElementById("save_mod_tariff_option");
  tariff_save_option.style.display = "block";
  var save_name_input = document.getElementById("save_mod_tariff_name");
  var current_name = document.getElementById("name_value");
  save_name_input.value = current_name.innerHTML + " v2"
}

var reset_case_tariff_info_from_button = function(info_button){
        var case_name = $(info_button).attr('value');
        get_and_display_case_tariff_info(case_name);
        get_and_display_case_load_info(case_name);
        get_and_display_case_demo_info(case_name);
}

var get_and_display_case_tariff_info = function(case_name){
    // Get tariff info for case.
    $.ajax({
        url: '/get_case_tariff',
        data: JSON.stringify(case_name),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        // Call the function to display the selected tariffs info
        success: function(data){display_case_tariff_info(case_name, data);},
        error: function(a,b,c){console.log(b); console.log(c);}
    });
}

var display_case_tariff_info = function(case_name, tariff_data){
    component = Object.keys(tariff_data['Parameters'])[0];
    display_table_data('info', tariff_data['Parameters'][component], true);
    $('#tariff_info_case').text(case_name);
    $('#tariff_info_name').text(tariff_data['Name']);
    $('#tariff_info_type').text(tariff_data['Type']);
    $('#tariff_info_state').text(tariff_data['State']);
    $('#tariff_info_component').text(component);
    $('#tariff_info_daily_charge').text(tariff_data['Parameters'][component]['Daily']['Value']);
    if ('Energy' in tariff_data['Parameters'][component]){
        $('#tariff_info_energy_charge').text(tariff_data['Parameters'][component]['Energy']['Value']);
    } else {
        $('#tariff_info_energy_charge').text('')
    }
    $("#info_tariff_summary_labels").css("display", "block");
}