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

var save_project = function(){
    $.ajax({
        url: '/save_project',
        contentType: 'application/json;',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            $('#message_dialog').dialog({modal: true});
            $('#message_dialog p').text(data['message']);

        }
    });
};

var save_project_as = function(){
    $.ajax({
        url: '/save_project_as',
        contentType: 'application/json;',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            $('#message_dialog').dialog({modal: true});
            $('#message_dialog p').text(data['message']);
            $('#project_name').text(data['name']);
        }
    });
};

var delete_project = function(){
    $.ajax({
        url: '/delete_project',
        contentType: 'application/json;',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            $('#message_dialog').dialog({modal: true});
            $('#message_dialog p').text(data['message']);
        }
    });
};

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