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
        // Call the function to update the drop downs with the new options.
        success: function(data){build_tables(data);}
    });

}

var build_tables = function(tariff_data){
    for (var key in tariff_data) {
        if (tariff_data.hasOwnProperty(key)) {
            build_table(tariff_data[key]);
        }
    }
}

var build_table = function(tariff_data){
    build_header(tariff_data['table_data']['table_header'])
    for (var key in tariff_data['table_data']['table_rows']){
        if (tariff_data['table_data']['table_rows'].hasOwnProperty(key)) {
            build_row(tariff_data['table_data']['table_rows'][key], 'DUOS_tariff_table')
        }
    }
    var tariff_table = document.getElementById('DUOS_tariff_table');
    tariff_table.style.height = (tariff_data['table_data']['table_rows'].length * 15).toString() + "px"
}

var build_header = function(header_data){
    var length_row = header_data.length
    for (var i = 0; i < length_row; i++){
        var th = document.createElement('th');
        var text = document.createTextNode(header_data[i]);
        th.appendChild(text);
        th.style.width = (100).toString() + "px"
        var header_row = document.getElementById('DUOS_tariff_table_header');
        header_row.appendChild(th);
    }
    var DUOS_tariff_table_header = document.getElementById('DUOS_tariff_table_header');
    DUOS_tariff_table_header.style.width = (length_row * 100).toString() + "px"
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
    var tariff_table = document.getElementById(table_id);
    tariff_table.appendChild(tr);
    tariff_table.style.width = (length_row * 100).toString() + "px"
}

// Get the options every time someone updates a tariff drop down.
$('#select_tariff').on('change', function() {
    console.log('try and load tariff')
    get_tariff();
});