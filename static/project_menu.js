var load_project = function(){
    $.ajax({
        url: '/load_project',
        contentType: 'application/json;',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            $('#message_dialog').dialog({modal: true});
            $('#message_dialog p').text(data['message']);
            $('#project_name').text(data['name']);
            $('#case_list').empty();
            clear_all_case_info();
            $('#results_status_not_set').show()
            $('#results_status_set').hide()
            $.each(data['cases'], function(i, case_name){
                add_case_to_gui(case_name);
                update_single_case_selector();
                reset_case_info(case_name);
                // Update menu bar status indicator
                $('#results_status_not_set').hide()
                $('#results_status_set').show()
            });
            plot_results();
        }
    });
};

var save_project_as = function(project_name){
    saveAs('/save_project/' + project_name, project_name +'.tda_results');
    $.ajax({
        url: '/current_project_name/project_name',
        contentType: 'application/json;',
        type : 'POST',
        dataType:"json",
        success: function(data){
            alert_user_if_error(data);
            $('#message_dialog').dialog({modal: true});
            $('#message_dialog p').text(data['message']);
            $('#project_name').text(data['name']);
        }
    });
};

var launch_project_namer = function(){
    if ($('#project_name').text() == 'N/A'){
        $('#project_name_input').val('New project')
    } else {
        $('#project_name_input').val($('#project_name').text())
    }
    $("#project_namer").dialog({
        modal: true,
        buttons: {"Save project": function(){
            $('#project_name').text($('#project_name_input').val())
            save_project_as($('#project_name_input').val())
            $("#project_namer").dialog('close')
            }
        }
    });
}

var restart_tool = function(){
    $.ajax({
        url: '/restart_tool',
        contentType: 'application/json;',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(message){
            window.onbeforeunload = function(){}
            location.reload();
            window.onbeforeunload = closingCode;
        }
    });
};