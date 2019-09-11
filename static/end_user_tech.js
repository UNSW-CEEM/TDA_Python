var create_end_user_tech_from_sample_from_gui = function(){

    var message = ""
    var file_name_set = $('#select').children("option:selected").val() != 'Select one';
    if (!file_name_set){
       message = "Please select load profiles before attempting to create a tech sample."
    }

    if (message != ""){
        $("#message_dialog").dialog({ modal: true});
        $("#message_dialog p").text(message)
    } else  {
        var tech_details = {}
        tech_details['tech_inputs'] = {}
        tech_details['tech_inputs']['solar'] = get_input_set_from_gui('solar');
        tech_details['tech_inputs']['battery'] = get_input_set_from_gui('battery');
        tech_details['tech_inputs']['demand_response'] = get_input_set_from_gui('demand_response');
        tech_details['load_details'] = get_load_details_from_ui();

        // Get chart data
        $.ajax({
            url: '/create_end_user_tech_from_sample_from_gui',
            data: JSON.stringify(tech_details),
            contentType: 'application/json',
            type : 'POST',
            async: 'false',
            dataType:"json",
            success: function(data){
                alert_user_if_error(data);
                $('#tech_status_not_set').hide();
                $('#tech_status_set').show();
                $('#tech_from_gui_status_not_set').hide();
                $('#tech_from_gui_status_set').show();
                $('#tech_from_file_status_set').hide();
                $('#tech_from_file_status_not_set').show();
                $('#net_load_profiles_status_not_set').hide();
                $('#net_load_profiles_status_set').show();
                $('#tech_sample_saved_status_not_set').show();
                $('#tech_sample_saved_status_set').hide();
                $('#calc_net_profiles').prop('disabled', false)
                $('#save_tech_sample').prop('disabled', false)
            }
        });
    }
}

var load_end_user_tech_from_sample_from_file = function(){
    $('#select').val('Select one').change();
    // Get chart data
    $.ajax({
        url: '/load_end_user_tech_from_sample_from_file',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            alert_user_if_error(data);
            insert_input_set_into_gui('solar', data['tech_inputs']['solar']);
            insert_input_set_into_gui('battery', data['tech_inputs']['battery']);
            insert_input_set_into_gui('demand_response', data['tech_inputs']['demand_response']);
            $('#tech_status_not_set').hide();
            $('#tech_status_set').show();
            $('#tech_from_gui_status_set').hide();
            $('#tech_from_gui_status_not_set').show();
            $('#tech_from_file_status_not_set').hide();
            $('#tech_from_file_status_set').show();
            $('#net_load_profiles_status_not_set').hide();
            $('#net_load_profiles_status_set').show();
            $('#tech_sample_saved_status_not_set').hide();
            $('#tech_sample_saved_status_set').show();
            $('#calc_net_profiles').prop('disabled', false)
            $('#save_tech_sample').prop('disabled', false)
        }
    });
}

var calc_sample_net_load_profiles = function(){
    var tech_details = {}
    tech_details['tech_inputs'] = {}
    tech_details['tech_inputs']['solar'] = get_input_set_from_gui('solar');
    tech_details['tech_inputs']['battery'] = get_input_set_from_gui('battery');
    tech_details['tech_inputs']['demand_response'] = get_input_set_from_gui('demand_response');

    // Get chart data
    $.ajax({
        url: '/calc_sample_net_load_profiles',
        data: JSON.stringify(tech_details),
        contentType: 'application/json',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            alert_user_if_error(data);
            $('#net_load_profiles_status_not_set').hide();
            $('#net_load_profiles_status_set').show();
            $('#tech_status_not_set').hide();
            $('#tech_status_set').show();
        }
    });
}

var save_end_user_tech_sample = function(){
    var tech_details = {}
    tech_details['tech_inputs'] = {}
    tech_details['tech_inputs']['solar'] = get_input_set_from_gui('solar');
    tech_details['tech_inputs']['battery'] = get_input_set_from_gui('battery');
    tech_details['tech_inputs']['demand_response'] = get_input_set_from_gui('demand_response');

    // Get chart data
    $.ajax({
        url: '/save_end_user_tech_sample',
        data: JSON.stringify(tech_details),
        contentType: 'application/json',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            alert_user_if_error(data);
            if (data['message'] == 'saved'){
                $('#tech_sample_saved_status_not_set').hide();
                $('#tech_sample_saved_status_set').show();
            }
        }
    });
}

var get_input_set_from_gui = function(type){
    var inputs = $('.{}_inputs'.replace('{}', type)).children();
    var input_object = {}
    $.each(inputs, function(i, input){
        input_object[$(input).prop('name')] = $(input).val();
    });
    return input_object
}

var insert_input_set_into_gui = function(type, input_set){
    $.each(input_set, function(name, input){
        $('.{a}_inputs [name=\"{b}\"]'.replace('{a}', type).replace('{b}', name)).val(input);
    });
}

$('.operational_parameter').on('change', function(){
    $('#tech_status_set').hide();
    $('#tech_status_not_set').show();
    $('#net_load_profiles_status_set').hide();
    $('#net_load_profiles_status_not_set').show();
    $('#tech_sample_saved_status_set').hide();
    $('#tech_sample_saved_status_not_set').show();
});

$('.sample_parameter').on('change', function(){
    $('#tech_status_set').hide();
    $('#tech_status_not_set').show();
    $('#tech_from_gui_status_set').hide();
    $('#tech_from_gui_status_not_set').show();
    $('#tech_from_file_status_set').hide();
    $('#tech_from_file_status_not_set').show();
    $('#net_load_profiles_status_set').hide();
    $('#net_load_profiles_status_not_set').show();
    $('#tech_sample_saved_status_set').hide();
    $('#tech_sample_saved_status_not_set').show();
    $('#calc_net_profiles').prop('disabled', true)
    $('#save_tech_sample').prop('disabled', true)
});


$('#calc_net_profiles').prop('disabled', true)
$('#save_tech_sample').prop('disabled', true)

