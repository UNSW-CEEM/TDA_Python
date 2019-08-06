$(function(){

    $("ul.dropdown li").hover(function(){
    
        $(this).addClass("hover");
        $('ul:first',this).css('display', 'block');
    
    }, function(){
    
        $(this).removeClass("hover");
        $('ul:first',this).css('display', 'none');
    
    });
    
    $("ul.dropdown li ul li:has(ul)").find("a:first").append(" &raquo; ");

});


// Does not work
var close_menu = function(){
    var all_drop_down_elements = $('.sub_menu ul:first')
    $.each(all_drop_down_elements, function(i, element){
        $(element).css('display', 'none');
    });
}