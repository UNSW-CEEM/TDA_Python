// This script gets the different load options and puts them in the load selector
$.getJSON("/load_names", function(json){
        $('#select').empty();
        $('#select').append($('<option>').text("Select1"));
        $.each(json, function(i, obj){
                $('#select').append($('<option>').text(obj));
        });
});
