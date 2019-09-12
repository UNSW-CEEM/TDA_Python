var choose_data_to_delete = function(){
    // Update the select box in the dialog to have the same options as the load select box on
    // the load tab.
    $('#delete_dialog select').empty();
    var load_options = $('#select option')
    $.each(load_options, function(i, option){
        $('#delete_dialog select').append($(option).clone());
    });
    $('#delete_dialog select').val('Select one');
    // Get the user to select which load data set to delete.
    $('#delete_dialog').dialog({modal: true,
        buttons: {"Delete": delete_data,
                  "Cancel": function(){$('#delete_dialog').dialog('close')}
                  }
    });
}

var delete_data = function(){
    // Get the selected load file to delete
    var file_name = $('#delete_dialog select').children("option:selected").val();

    // Send an instruction to the server to delete the load file.
    request = {'name': file_name}
    $.ajax({
        url: '/delete_load_data',
        type: 'POST',
        data: JSON.stringify(request),
        contentType: 'application/json;',
        async: 'false',
        dataType:"json",
        success: function(data){
            alert_user_if_error(data);
            $('#delete_dialog').dialog('close');
            $('#message_dialog').dialog({modal: true})
            $('#message_dialog p').text(data['message'])
        }
    });
};

var import_data = function(data_type, call_back){

    // Action to perform when the user chooses the create now option.
    var create_now = function(){
        $.ajax({
            url: '/import_load',
            contentType: 'application/json;',
            data: JSON.stringify({'type': data_type}),
            type : 'POST',
            async: 'false',
            dataType:"json",
            success: function(data){
                alert_user_if_error(data);
                $('#import_dialog').dialog('close');
                if ('message' in data){
                    $('#message_dialog').dialog({modal: true});
                    $('#message_dialog p').text(data['message']);
                    if (call_back !== undefined){
                        call_back(data['name']);
                    }
                }
            }
        });
    }

    // Action to perform when the user chooses to view the sample load.
    var open_sample = function(){
        $.ajax({
            url: '/open_sample',
            data: JSON.stringify(data_type),
            contentType: 'application/json;',
            type : 'POST',
            async: 'false',
            dataType:"json",
            success: function(data){
                alert_user_if_error(message)
                $('#import_dialog').dialog('close');
                $('#message_dialog').dialog({modal: true});
                $('#message_dialog p').text(data['message']);
            }
        });
    }

    // Opening the initial import dialog.
    $('#import_dialog').dialog({
        modal: true,
        width: 500,
        buttons: {"Create now": create_now,
                  "Open sample file": open_sample,
                  "Cancel": function(){$('#import_dialog').dialog('close')}}
    });
    var message = "Please refer to the instructions, section 5.3 (CREATING NEW LOAD DATA) and put the network load " +
                  "data in the required format before importing. You can also open the sample file and see the " +
                  "required or paste in your data into this file and save as a new load file and then load the file " +
                  "when creating the new load data."
    $('#import_dialog p').text(message)
}

var restore_original_data_set = function(){
    $('#message_dialog').dialog({modal: true});
    $('#message_dialog p').text("Restoring data sets.")
    $.ajax({
        url: '/restore_original_data_set',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            alert_user_if_error(data)
            $('#message_dialog p').text(data['message'])
        }
    });
};