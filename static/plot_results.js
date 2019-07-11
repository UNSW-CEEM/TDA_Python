
var add_case = function(){
    // Get the name of the selected tariff.
    tariff_name = $('#select_tariff').val();

    // Get load details
    load_request = get_load_details_from_ui();

    // Bundle case details into a single object
    case_details = {'case_name': "dummy_case",
                    'tariff_name': tariff_name,
                    'load_details': load_request};

    // Get the python app to create the case and calculate results
    $.ajax({
        url: '/add_case',
        data: JSON.stringify(case_details),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){plot_results()}
    });

}

var plot_results = function(){

    // Define the chart layout
    var layout = {autosize: true,
                  margin: { l: 40, r: 35, b: 40, t: 20, pad: 0 },
                  paper_bgcolor: '#EEEEEE',
                  plot_bgcolor: '#c7c7c7',
                  showlegend: true};

    // Get chart data
    $.ajax({
        url: '/get_results',
        data: JSON.stringify(case_details),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            Plotly.newPlot('result_chart', response, layout);
        ;}
    });

}