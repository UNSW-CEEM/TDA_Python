var export_results = function(){
    $.ajax({
        url: '/export_results',
        contentType: 'application/json;',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            $('#message_dialog').dialog({modal: true});
            $('#message_dialog p').text(data['message']);
        }
    });
};