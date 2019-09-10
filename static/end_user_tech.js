var add_end_user_tech_from_gui = function(){

    var tech_details = {}
    tech_details['solar_inputs'] = get_input_set_from_gui('solar');
    tech_details['battery_inputs'] = get_input_set_from_gui('battery');
    tech_details['demand_response_inputs'] = get_input_set_from_gui('demand_response');
    tech_details['load_details'] = get_load_details_from_ui();

    // Get chart data
    $.ajax({
        url: '/add_end_user_tech_from_gui',
        data: JSON.stringify(tech_details),
        contentType: 'application/json',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            alert_user_if_error(data);
            $('#tech_status_not_set').hide();
            $('#tech_status_set').show();
        }
    });

}

var get_input_set_from_gui = function(type){
    var inputs = $('.{}_inputs .input_stacked'.replace('{}', type));
    var input_object = {}
    $.each(inputs, function(i, input){
        input_object[$(input).prop('name')] = $(input).val();
    });
    return input_object
}

var add_end_user_tech_from_file = function(){
    $('#select').val('Select one').change();
    // Get chart data
    $.ajax({
        url: '/add_end_user_tech_from_file',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            alert_user_if_error(data);
            $('#tech_status_not_set').hide();
            $('#tech_status_set').show();
        }
    });
}

var save_end_user_tech_sample = function(){
    // Get chart data
    $.ajax({
        url: '/save_end_user_tech_sample',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            alert_user_if_error(data);
        }
    });
}