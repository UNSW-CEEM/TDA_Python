
$( ".chart" ).contextmenu(event, function() {
    event.preventDefault();
    ask_for_export_type(event)
});

var ask_for_export_type = function(event){
    var chart_id = $(event.target).closest("div[id]").attr('id')
    $( "#message_dialog" ).dialog({
        modal: true,
        buttons: {"Export": function(){export_chart_to_excel(chart_id)},
                  "Cancel": function(){$( "#message_dialog" ).close()}},
        position: {my: 'left', at: 'right', of: event}
    });
};

var copy_data = function(chart_id){
    ;
};

var export_chart_to_excel = function(chart_id){
    var chart_data = document.getElementById(chart_id).data
}