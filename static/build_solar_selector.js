var add_solar_names = function(data){
    $.getJSON("/solar_names", function(json){
        $('#solar_data').empty();
        $.each(json, function(i, obj){
            $('#solar_data').append($('<option>').text(obj));
        });
    });
}
add_solar_names();