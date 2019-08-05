var update_check_list = function(event, called_from){
    var options = $('.' + $(called_from).attr('class').replace(' ', '.'));
    $.each(options, function(i, option){
        if ($(option).is(":checked") & $(option).attr('value') !== $(called_from).attr('value')){
            $(option).prop("checked", false);
        };
    });
}