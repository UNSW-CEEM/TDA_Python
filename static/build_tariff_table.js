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
    console.log('try and load tariff 2')
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
            display_table_and_charge_data(key, tariff_data['Parameters'][key]);
        }
    }
}

var display_table_and_charge_data = function(table_name, tariff_data){

    document.getElementById(table_name + "_daily_charge").value = tariff_data['Daily']['Value'];
    if ('Energy' in tariff_data){
        document.getElementById(table_name + "_energy_charge").value = tariff_data['Daily']['Value'];
    }

    if ( $.fn.dataTable.isDataTable( '#' + table_name + '_tariff_table' ) ) {
        var table = $('#' + table_name + '_tariff_table').DataTable();
        table.MakeCellsEditable("destroy");
        $('#' + table_name + '_tariff_table').DataTable().destroy();
    }

    $('#' + table_name + '_tariff_table' + ' tr').remove();

    build_header(table_name, tariff_data['table_data']['table_header'])

    for (var key in tariff_data['table_data']['table_rows']){
        if (tariff_data['table_data']['table_rows'].hasOwnProperty(key)) {
            build_row(tariff_data['table_data']['table_rows'][key], table_name + '_tariff_table')
        }
    }
    var tariff_table = document.getElementById( table_name + '_tariff_table');
    //tariff_table.style.height = (tariff_data['table_data']['table_rows'].length * 15).toString() + "px"
    $(document).ready(function() {
        $('#' + table_name + '_tariff_table').DataTable( {
            "scrollY": '30vh',
            "scrollX": true,
            "paging": true,
            "info": true,
            "filter": false,
            "retrieve": true

        } );
    } );

    var table = $('#' + table_name + '_tariff_table').DataTable();
    table.MakeCellsEditable({"onUpdate": display_save_mod_tariff_option});

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

function display_save_mod_tariff_option() {
  var tariff_save_option = document.getElementById("save_mod_tariff_option");
  tariff_save_option.style.display = "block";
  var save_name_input = document.getElementById("save_mod_tariff_name");
  var current_name = document.getElementById("name_value");
  save_name_input.value = current_name.innerHTML + " v2"
}