var create_end_user_tech_from_sample_from_gui = function(){
    var file_name_set = $('#select').val() != 'Select one';
    if (!file_name_set){
        var message = "Please select load profiles before attempting to create a tech sample."
        $("#message_dialog").dialog({ modal: true});
        $("#message_dialog p").text(message)
    } else  {
        var message = "Creating end user tech sample."
        $("#message_dialog").dialog({ modal: true});
        $("#message_dialog p").text(message)
        var tech_details = {'tech_inputs': get_all_tech_inputs(),
                            'load_details': get_load_details_from_ui()}
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
                get_net_load_chart();
                status_set(['tech', 'tech_from_gui', 'net_load_profiles'])
                status_not_set(['tech_from_file', 'tech_sample_saved'])
                $('#calc_net_profiles').prop('disabled', false)
                $('#save_tech_sample').prop('disabled', false)
                $("#message_dialog p").text(data['message'])
            }
        });
    }
}

var load_end_user_tech_from_sample_from_file = function(){
    $('#select').val('Select one').change();
    var message = "Loading end user tech sample."
    $("#message_dialog").dialog({ modal: true});
    $("#message_dialog p").text(message)
    // Get chart data
    $.ajax({
        url: '/load_end_user_tech_from_sample_from_file',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            alert_user_if_error(data);
            if ('message' in data){
                insert_input_set_into_gui('solar', data['tech_inputs']['solar']);
                insert_input_set_into_gui('battery', data['tech_inputs']['battery']);
                insert_input_set_into_gui('demand_response', data['tech_inputs']['demand_response']);
                get_net_load_chart();
                status_set(['tech', 'tech_from_file', 'net_load_profiles', 'tech_sample_saved'])
                status_not_set(['tech_from_gui'])
                $('#calc_net_profiles').prop('disabled', false)
                $('#save_tech_sample').prop('disabled', false)
                $("#message_dialog p").text(data['message'])
            } else {
                $("#message_dialog").dialog('close');
            }
        }
    });
}

var calc_sample_net_load_profiles = function(){
    var message = "Calculating net load profiles."
    $("#message_dialog").dialog({ modal: true});
    $("#message_dialog p").text(message)
    var tech_details = {'tech_inputs': get_all_tech_inputs()}
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
            get_net_load_chart();
            status_set(['tech', 'net_load_profiles'])
            $("#message_dialog p").text(data['message'])
        }
    });
}

var save_end_user_tech_sample = function(){
    var message = "Saving end user tech sample."
    $("#message_dialog").dialog({ modal: true});
    $("#message_dialog p").text(message)
    var tech_details = {'tech_inputs': get_all_tech_inputs()}
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
                status_set(['tech_sample_saved'])
                $("#message_dialog p").text(data['message'])
            }
        }
    });
}

var get_net_load_chart =  function(){
    // Update menu bat status indicator
    var load_request = {'chart_type': $('#select_net_graph').val()}
    $.ajax({
    url: '/net_load_chart_data',
    data: JSON.stringify(load_request),
    contentType: 'application/json;',
    type : 'POST',
    async: 'false',
    dataType:"json",
    success: function(data){
            alert_user_if_error(data)
            plot_net_load(data);
        }
    });
}

var plot_net_load = function(response){
    var layout = {autosize: true,
                  margin: { l: 40, r: 35, b: 40, t: 20, pad: 0 },
                  paper_bgcolor: '#EEEEEE',
                  plot_bgcolor: '#c7c7c7',
                  showlegend: response['chart_data']['layout'].showlegend,
                  xaxis: response['chart_data']['layout'].xaxis,
                  yaxis: response['chart_data']['layout'].yaxis};
    Plotly.newPlot('net_load_chart', response['chart_data']['data'], layout);
}

$('.operational_parameter').on('change', function(){
    status_not_set(['tech', 'net_load_profiles', 'tech_sample_saved'])
});

$('.sample_parameter').on('change', function(){
    status_not_set(['tech', 'net_load_profiles', 'tech_sample_saved', 'tech_from_gui',
                    'tech_from_file'])
    $('#calc_net_profiles').prop('disabled', true)
    $('#save_tech_sample').prop('disabled', true)
});

$('#select_net_graph').on('change', function(){
    get_net_load_chart();
});

$('#calc_net_profiles').prop('disabled', true)
$('#save_tech_sample').prop('disabled', true)

var get_all_tech_inputs = function(){
    var tech_inputs = {}
    tech_inputs['solar'] = get_input_set_from_gui('solar');
    tech_inputs['battery'] = get_input_set_from_gui('battery');
    tech_inputs['demand_response'] = get_input_set_from_gui('demand_response');
    return tech_inputs
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

var status_set = function(base_ids){
    $.each(base_ids, function(i, base_id){
         $('#' + base_id +  '_status_set').show();
         $('#' + base_id + '_status_not_set').hide();
    });
}

var status_not_set = function(base_ids){
    $.each(base_ids, function(i, base_id){
         $('#' + base_id +  '_status_set').hide();
         $('#' + base_id + '_status_not_set').show();
    });
}

