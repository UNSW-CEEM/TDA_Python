var export_results = function(){
    $('#message_dialog').dialog({modal: true});
    $('#message_dialog p').text('Exporting . . .');
    $.ajax({
        url: '/export_results',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            $('#message_dialog').dialog({modal: true});
            $('#message_dialog p').text(data);
        }
    });
};