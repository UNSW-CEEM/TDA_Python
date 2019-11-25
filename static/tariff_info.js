var open_tariff_info = function(){

    var open_generic = function(tariff_type){
        $('#message_dialog p').text("Opening tariff info.")
        if (tariff_type == 'network'){
            var name = $('#network_tariff_selection_panel .select_tariff').val();
        } else {
            var name = $('#retail_tariff_selection_panel .select_tariff').val();
        }
        if (name != 'None'){
            $.ajax({
                url: '/open_tariff_info',
                type : 'POST',
                data: JSON.stringify({'name': name, 'tariff_type': tariff_type}),
                contentType: 'application/json;',
                async: 'false',
                dataType:"json",
                success: function(data){
                    alert_user_if_error(data);
                    $('#message_dialog p').text(data['message'])
                }
            });
        } else {
            $('#message_dialog p').text('Please close this dialog, select a ' + tariff_type + ' tariff and try again.')
        }
    }

    var open_network = function(){
        return open_generic('network')
    }

    var open_retail = function(){
        return open_generic('retail')
    }

    $('#message_dialog').dialog({modal: true,
                                 buttons: {'Network': open_network, 'Retail': open_retail}});
    $('#message_dialog p').text("Please choose a tariff type.")
};