var import_data = function(type, version){
    $('#dialog').dialog({modal: true});
    $.ajax({
        url: '/import_load_data',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(){
            $('#updating_tariffs p').text(data)
        }
    });

};

var delete_data = function(type, version){
    $('#dialog').dialog({modal: true});
    $.ajax({
        url: '/delete_load_data',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(){
            $('#updating_tariffs p').text(data)
        }
    });
};