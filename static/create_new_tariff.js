
var launch_tariff_creator = function(){
    $( "#create_tariff_popup" ).dialog({
        modal: true,
        buttons: {"Continue": function(){enable_tariff_creation()},
                  "Cancel": function(){$('#create_tariff_popup').dialog('close');}}
    });
}

var enable_tariff_creation = function(){
    // Change selected tariff to none
    $('.select_tariff').val('None');
    $('.tariff_label').html('N/A');
    // Add a button to enable the user to add components to their tariff
    var parameter_types = $('.table_set')
    $.each(parameter_types, function(i, parameter_type){
        $("#" + $(parameter_type).prop('id')).empty()
    })
    $('.component_adder').show();
    $('#create_tariff_popup').dialog('close');
    $('#tariff_panel_button').click();
}

var disable_tariff_creation = function(){
}


var get_component_type = function(tariff_type_panel){
    build_component_template_option();
    $( "#choose_component_type" ).dialog({
        modal: true,
        buttons: {"Continue": function(){add_component(tariff_type_panel)},
                  "Cancel": function(){$('#choose_component_type').dialog('close');}}
    });
}

var add_component = function(tariff_type_panel){
    var component_type = $('#choose_component_type select');
    templates = component_templates();
    $('#choose_component_type').dialog('close');
    parameter_types = $('#' + tariff_type_panel + ' .table_set')
    var to_insert = {[component_type.val()]: templates[component_type.val()]}
    $.each(parameter_types, function(i, parameter_type){
        var parameter_type_id = $(parameter_type).prop('id')
        display_tables(tariff_type_panel, parameter_type_id, to_insert, true, false);
    })
    set_save_button_to_alert_state(tariff_type_panel);
}

var component_templates = function(){
    var daily = {'table_header': ['Unit', 'Value'], 'table_rows': [['$/day', '1.0']]}
    var seasonal_tou = {'table_header': ['Name', 'Month', 'Unit' ,'Value'],
                        'table_rows': [['Summer', '[12, 1, 2]', '$/kWh', '1.0']]}
    var tou = {'table_header': ['Name', 'Month', 'TimeIntervals', 'Unit' ,'Value', 'Weekday', 'Weekend'],
               'table_rows': [['Summer peak workdays', '[12, 1, 2]', '{\'T1\': [\'15:00\', \'23:00\']}', '$/kWh', '1.0',
                               'true', 'false']]}
    var demand = {'table_header': ['Name', 'Day Average', 'Demand Window Length', 'Min Demand Window (kW)',
                                   'Min Demand Charge ($)', 'Month', 'Number of Peaks', 'TimeIntervals', 'Unit'
                                   ,'Value', 'Weekday', 'Weekend'],
                  'table_rows': [['Summer peak workdays', 'true', '1', '0', '0', '[12, 1, 2]', '1',
                                  '{\'T1\': [\'15:00\', \'23:00\']}', '$/kW/Day', '1.0', 'true', 'false']]}
    var flat_rate = {'table_header': ['Unit', 'Value'], 'table_rows': [['$/kWh', '1.0']]}
    var block_annual = {'table_header': ['Name', 'HighBound', 'Unit' ,'Value'],
                        'table_rows': [['Summer', '1000', '$/kWh', '1.0']]}
    var block_quarterly = {'table_header': ['Name', 'HighBound', 'Unit' ,'Value'],
                           'table_rows': [['Summer', '1000', '$/kWh', '1.0']]}
    var templates = {'Daily': daily, 'FlatRate': flat_rate, 'FlatRateSeasonal': seasonal_tou, 'TOU': tou,
                     'Demand': demand, 'BlockAnnual': block_annual, 'BlockQuarterly': block_quarterly}
    return templates
}

var build_component_template_option = function(){
    templates = component_templates();
    $('#choose_component_type select').empty()
    for (var component_name in templates){
            $('#choose_component_type select').append(new Option(component_name, component_name));
    }
}

