var update_check_list = function(event, called_from){
    var options = $('.down_sample_option');
    $.each(options, function(i, option){
        if ($(option).is(":checked") & $(option).attr('value') !== $(called_from).attr('value')){
            $(option).attr("checked", false);
        };
    });
}