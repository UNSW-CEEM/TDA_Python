
$( ".chart" ).contextmenu(event, function() {
    event.preventDefault();
    ask_for_export_type($(event.target).closest("div[id]").attr('id'))
});

var ask_for_export_type = function(chart_id){
    $( "#message_dialog" ).dialog({
        modal: true,
        width: 500,
        buttons: {"Copy to clipboard": function(){copy_data(chart_id)},
                  "Export to csv": function(){}}
    });
};

var copy_data = function(chart_id){
    $( "#message_dialog" ).text(chart_id)
};