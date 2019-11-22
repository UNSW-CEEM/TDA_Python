var export_results = function(){
    $('#message_dialog').dialog({modal: true});
    $('#message_dialog p').text('Exporting . . .');
    $.ajax({
        url: '/prepare_export_results',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            alert_user_if_error(data);
            $('#message_dialog').dialog({modal: true});
            $('#message_dialog p').text(data['message']);
            saveAs('/export_results', 'results.xlsx');
        }
    });
};