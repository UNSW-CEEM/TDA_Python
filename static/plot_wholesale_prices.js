
var get_and_plot_wholesale_prices = function(){

    var year = $('#select_wholesale_year').val();

    var state = $('#select_wholesale_state').val();

    var chart_type = $('#select_price_graph').val();

    $('#dialog').dialog({modal: true});

    var price_request = {'year': year, 'state': state, 'chart_type': chart_type};

    $.ajax({
        url: '/wholesale_prices',
        data: JSON.stringify(price_request),
        contentType: 'application/json;',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            plot_wholesale_prices(data);
        }
    });

    if (year != 'None' && state != 'None'){
        $('#prices_status_not_set').hide()
        $('#prices_status_set').show()
    } else {
        $('#prices_status_not_set').show()
        $('#prices_status_set').hide()
    }

}

var plot_wholesale_prices = function(chart_data){
    Plotly.newPlot('price_chart', chart_data['data'], chart_data['layout'], {responsive: true});
    $('#dialog').dialog('close');
}

var get_wholesale_price_options = function(){

    $.ajax({
        url: '/wholesale_price_options',
        contentType: 'application/json;',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            add_option('#select_wholesale_year', data['years'])
            add_option('#select_wholesale_state', data['states'])
        }
    });
}

var add_option = function(option_identifier, options){
    $(option_identifier).empty();
    $(option_identifier).append($('<option>').text("None"));
    $.each(options, function(i, option){
            $(option_identifier).append($('<option>').text(option));
    });
}

get_wholesale_price_options();

$('.wholesale_filter').on('change', function() {
    get_and_plot_wholesale_prices();
});

$('#select_price_graph').on('change', function() {
    get_and_plot_wholesale_prices();
});


get_and_plot_wholesale_prices();