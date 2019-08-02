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