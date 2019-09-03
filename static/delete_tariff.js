var delete_tariff = function(evt, div_that_got_clicked){
    console.log('tried to delete')
    var tariff_type_tab_id = $(div_that_got_clicked).closest('[id]').attr('id');
    // Get the name of the selected tariff.
    var tariff_name = $('#' + tariff_type_tab_id + ' .select_tariff').val();

    var request_details = {
        'tariff_panel': tariff_type_tab_id,
        'tariff_name': tariff_name
    }

    // Ask for the corresponding json.
    $.ajax({
        url: '/delete_tariff',
        data: JSON.stringify(request_details),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(){
            alert_user_if_error(data);
            reset_tariff_options(tariff_type_tab_id);
            tear_down_tables_in_tariff_type_panel(tariff_type_tab_id);
            }
    });
}