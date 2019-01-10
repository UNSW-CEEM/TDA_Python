// THis is javascript's 'print' function - you can open up your js console in your browser and see them.
console.log('Hi im javascript options');

// This is a jquery function that visits the '/data' endpoint. See run.py  (or try in your browser)
$.getJSON("/load_names", function(json){
        console.log(json);
        $('#select').empty();
        $('#select').append($('<option>').text("Select"));
        $.each(json, function(i, obj){
                $('#select').append($('<option>').text(obj));
        });
});
