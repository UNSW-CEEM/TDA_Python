
var launch_tariff_creator = function(){
    $( "#create_tariff_popup" ).dialog({
        modal: true,
        buttons: {"Continue": function(){enable_tariff_creation()},
                  "Cancel": function(){$('#create_tariff_popup').dialog('close');}}
    });
}

var enable_tariff_creation = function(){
    // Make the inputs for providing tariff details visible.
    $('.tariff_input').show();
    $('.tariff_label').hide();

    // Add a button to enable the user to add components to their tariff
    var parameter_types = $('.table_set')
    $.each(parameter_types, function(i, parameter_type){
        $("#" + $(parameter_type).prop('id')).empty()
    //    $("<div style='width: 100%; height: 15%'><button onclick=get_component_type(this)>&#10010; Add component</button></div>").
    //    appendTo($("#" + $(parameter_type).prop('id')))
    })
    $('.component_adder').show();
    $('#create_tariff_popup').dialog('close');
}

var disable_tariff_creation = function(){
    // Make the inputs for providing tariff details hidden.
    $('.tariff_input').hide();
    $('.tariff_label').show();
    //$('.component_adder').hide();
}


var get_component_type = function(tariff_type_panel){
    templates = component_templates();
    for (var component_name in templates){
        if (component_name)
        $('#choose_component_type select').append(new Option(component_name, component_name));
    }
    $( "#choose_component_type" ).dialog({
        modal: true,
        buttons: {"Continue": function(){add_component(tariff_type_panel)},
                  "Cancel": function(){$('#choose_component_type').dialog('close');}}
    });
}

var add_component = function(tariff_type_panel){
    var component_type = $('#choose_component_type select');
    templates = component_templates();
    console.log(component_type.val());
    $('#choose_component_type').dialog('close');
    parameter_types = $('#' + tariff_type_panel + ' .table_set')
    var to_insert = {[component_type.val()]: templates[component_type.val()]}
    $.each(parameter_types, function(i, parameter_type){
        var parameter_type_id = $(parameter_type).prop('id')
        display_tables(tariff_type_panel, parameter_type_id, to_insert, true, false);
    })

}

var component_templates = function(){
    var daily = {'table_header': ['Unit', 'Value'],
                 'table_rows': [['$/kWh', '1.0']]}
    var templates = {'Daily': daily}
    return templates
}