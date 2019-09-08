
var launch_tou_analysis = function(tariff_type_panel, parameter_type, table_name){

    var tariff_table_data = get_tariff_table_data(parameter_type, table_name)

    $.ajax({
        url: '/get_tou_analysis',
        data: JSON.stringify(tariff_table_data),
        contentType: 'application/json',
        type : 'POST',
        async: 'false',
        dataType:"json",
        // Call the function to display the selected tariffs info
        success: function(data){
            alert_user_if_error(data);
            $('#message_dialog').dialog({width: 600, height: 300});
            $('#message_dialog p').html(data['message'].replace(/\n/g, '<br />'))
        }
    });
}