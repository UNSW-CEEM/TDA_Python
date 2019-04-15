var plot_load = function(response){
    // Create a new line chart object where as first parameter we pass in a selector
    // that is resolving to our chart container element. The Second parameter
    // is the actual data object.
    console.log(response);
    var d = new Date();
    var t0 = d.getTime();
    var series_to_plot = [];
    var arraylength = response.Time.length
    for (var i = 0; i < arraylength; i++){
        var date_time = response.Time[i]
        var date = date_time.split(' ')[0]
        var time = date_time.split(' ')[1]
        var year = date.split('-')[0]
        var month = date.split('-')[1]
        var day = date.split('-')[2]
        //var hour = time.split(':')[0]
        //var minute = time.split(':')[1]
        //var second = time.split(':')[2]
        var date_time_obj = new Date(year, (month - 1), day)
        series_to_plot.push({x: date_time_obj, y: response.Mean[i]})
    }
    var t1 = d.getTime();
    var t01 = t1 - t0
    console.log(t01)
    var chart = new Chartist.Line('.ct-chart', {series: [{name: 'series1',data: series_to_plot}]},
      {axisX: { type: Chartist.FixedScaleAxis, divisor: 5, labelInterpolationFnc: function(value) {
          return moment(value).format('YYYY MMM D '); }}, showPoint: false, lineSmoothed: false}
      );
    var t2 = d.getTime();
    var t12 = t2 - t1
    console.log(t12)
  }

var add_demo_selectors = function(response){
    console.log(response)
    var arraylength = response.actual_names.length

    for (var i = 0; i < 10; i++){
        selector_id = "demo_select_" + i.toString()
        div_id = "demo_" + i.toString()
        label_id = "demo_label_" + i.toString()
        var label = document.getElementById(label_id);
        $('#'+div_id).hide()
        label.innerHTML = ''
    }

    for (var i = 0; i < arraylength; i++){
        selector_id = "demo_select_" + i.toString()
        label_id = "demo_label_" + i.toString()
        div_id = "demo_" + i.toString()
        $.each(response.options[response.actual_names[i]], function(i, obj){
                $('#'+selector_id).append($('<option>').text(obj));
        });
        var label = document.getElementById(label_id);
        $('#'+selector_id).val('All')
        $('#'+div_id).show()
        var name = response.display_names[response.actual_names[i]]
        label.innerHTML = name
    }
}

var plot_filtered_load = function(){

    var filter_options = {}

    for (var i = 0; i < 10; i++){
        selector_id = "demo_select_" + i.toString()
        label_id = "demo_label_" + i.toString()
        var label = document.getElementById(label_id);
        var values = $('#' + selector_id).val();
        filter_options[label.innerHTML] = values;
        console.log(values)
    }

    var file_name = $('#select').children("option:selected").val();

    var load_request = {'file_name': file_name, 'filter_options': filter_options}

    var layout = {autosize: true, margin: { l: 50, r: 20, b: 30, t: 20, pad: 10 },
                  paper_bgcolor: '#EEEEEE',
                  plot_bgcolor: '#c7c7c7'};

    $.ajax({
    url: '/filtered_load_data',
    data: JSON.stringify(load_request),
    contentType: 'application/json;charset=UTF-8',
    type : 'POST',
    async: 'false',
    success: function (data) {Plotly.newPlot('load_chart', data, layout);}
    });

    console.log("I sent the post")

}

var plot_unfiltered_load = function(response){
    var layout = {autosize: true, margin: { l: 50, r: 20, b: 30, t: 20, pad: 10 },
                  paper_bgcolor: '#EEEEEE',
                  plot_bgcolor: '#c7c7c7'};
    Plotly.newPlot('load_chart', response, layout);
    console.log("I sent the post")
}


$('#select').on('change', function() {
  var file_name = $('#select').children("option:selected").val();
  $.getJSON('/demo_options/' + file_name, add_demo_selectors);
  console.log("I saw the change 2")
  console.log("I saw the change 2")
  $.getJSON('/load_load/' + file_name, plot_unfiltered_load);
});


$('.get_filtered_load').on('click', function() {
    console.log("I saw the change")
    plot_filtered_load();
});

window.onresize = function() {
    Plotly.Plots.resize('load_chart');
};