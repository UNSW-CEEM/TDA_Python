
var get_and_plot_wholesale_prices = function(){

    var year = $('#select_wholesale_year').val();

    var state = $('#select_wholesale_state').val();

    $('#dialog').dialog({modal: true});

    var price_request = {'year': year, 'state': state};

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

}

var plot_wholesale_prices = function(chart_data){
    var layout = {margin: { l: 40, r: 35, b: 40, t: 20, pad: 0 },
                  paper_bgcolor: '#EEEEEE',
                  plot_bgcolor: '#c7c7c7',
                  showlegend: true};
    Plotly.newPlot('price_chart', chart_data, layout, {responsive: true});
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