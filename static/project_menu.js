var load_project = function(){
    $.ajax({
        url: '/load_project',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            $('#message_dialog').dialog({modal: true});
            $('#message_dialog p').text(data)
        }
    });
};