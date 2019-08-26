var add_end_user_tech = function(){

    var tech_details = {}
    tech_details['solar_inputs'] = get_input_set_from_gui('solar');
    tech_details['battery_inputs'] = get_input_set_from_gui('battery');
    tech_details['demand_response_inputs'] = get_input_set_from_gui('demand_response');

    // Get chart data
    $.ajax({
        url: '/add_end_user_tech',
        data: JSON.stringify(tech_details),
        contentType: 'application/json',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            $('#tech_status_not_set').hide()
            $('#tech_status_set').show()
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