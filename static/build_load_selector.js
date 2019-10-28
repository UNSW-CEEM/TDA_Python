// This script gets the different load options and puts them in the load selector
var add_load_names = function(){
    $.getJSON("/load_names", function(json){
            load_list = json['names']
            current_loaded_data = json['current_load']

            if (!load_list.includes(current_loaded_data)) {
                $('#select').empty();
                $('#select').append($('<option>').text("Select one"));
                $.each(json['names'], function(i, obj){
                    $('#select').append($('<option>').text(obj));
                });
            }
            else {
                $('#select').empty();
                $('#select').append($('<option>').text("Select one"));
                $.each(json['names'], function(i, obj){
                    $('#select').append($('<option>').text(obj));
                });
                $('#select').val(current_loaded_data)
            }
    });
}
add_load_names();