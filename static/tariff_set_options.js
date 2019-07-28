// This script gets the different tariff set options and puts them in the tariff menu
$.getJSON("/tariff_set_options/network", function(json){
        $('#network_tariff_sets').empty();
        $.each(json, function(i, obj){
                $('#network_tariff_sets').append($('<li><div id=' + obj +
                    ' onclick=reset_tariff_set("Network","' + obj +'")>' + obj + '</div></li>'));
        });
});

$.getJSON("/tariff_set_options/retail", function(json){
        $('#retail_tariff_sets').empty();
        $.each(json, function(i, obj){
                $('#retail_tariff_sets').append($('<li><div id=' + obj +
                    ' onclick=reset_tariff_set("Retail","' + obj +'")>' + obj + '</div></li>'));
        });
});

var reset_tariff_set = function(type, version){
    console.log('tried_to_reset_tariffs')
    request_details = {'type': type,
                       'version': version}
    // Get the server to reset the active tariff file
    $.ajax({
        url: '/set_tariff_set_in_use',
        data: JSON.stringify(request_details),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){}
    });
};
