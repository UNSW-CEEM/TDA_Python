var open_tariff_info = function(){
    $('#message_dialog').dialog({modal: true});
    $('#message_dialog p').text("Opening tariff info data.")
    $.ajax({
        url: '/open_tariff_info',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            alert_user_if_error(data);
            $('#message_dialog p').text(data['message'])
        }
    });
};