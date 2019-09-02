
$(".chart").contextmenu(event, function() {
    event.preventDefault();
    ask_for_export_type(event);
});

var ask_for_export_type = function(event){
    var chart_id = $(event.target).closest("div[id]").attr('id')
    $("#export_dialog").dialog({
        modal: true,
        buttons: {"Export to csv": function(){export_chart(chart_id, 'csv')},
                  "Copy to clipboard": function(){export_chart(chart_id, 'clipboard')},
                  "Cancel": function(){$("#export_dialog").dialog('close')}},
        position: {my: 'left', at: 'right', of: event}
    });
    $('#export_dialog p').text("Choose export type.");
};


var export_chart = function(chart_id, export_type){
    var request_details = {};
    request_details['chart_data'] = document.getElementById(chart_id).data;
    request_details['x_title'] = document.getElementById(chart_id).layout.xaxis.title.text;
    request_details['y_title'] = document.getElementById(chart_id).layout.yaxis.title.text;
    request_details['export_type'] = export_type;
    $('#export_dialog').dialog({modal: true});
    $('#export_dialog p').text("Preparing chart data export.");
    $.ajax({
    url: '/export_chart_data',
    data: JSON.stringify(request_details),
    contentType: 'application/json;',
    type : 'POST',
    async: 'false',
    dataType:"json",
    success: function(data){
        $("#export_dialog").dialog('close');
        $('#message_dialog').dialog({modal: true});
        $('#message_dialog p').text(data);
    }
    });
}