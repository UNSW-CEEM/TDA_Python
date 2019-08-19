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
            $.each(data['cases'], function(i, case_name){
                add_case_to_gui(case_name);
            });
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
        success: function(message){
            $('#message_dialog').dialog({modal: true});
            $('#message_dialog p').text(message);

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
        success: function(message){
            $('#message_dialog').dialog({modal: true});
            $('#message_dialog p').text(message);

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
        success: function(message){
            $('#message_dialog').dialog({modal: true});
            $('#message_dialog p').text(message);
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
            $('#message_dialog').dialog({modal: true});
            $('#message_dialog p').text(message);
            location.reload();
        }
    });
};