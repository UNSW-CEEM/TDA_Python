var import_data = function(type, version){
    $('#dialog').dialog({modal: true});
    $.ajax({
        url: '/import_load_data',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(){
            $('#dialog').dialog('close');
        }
    });

};