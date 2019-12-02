
var show_info = function(){
    $("#info_dialog").dialog();
}

var open_ceem_webpage = function(){
    $.ajax({url:'/open_ceem_webpage'})
}