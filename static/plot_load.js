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
    var chart = new Chartist.Line('.ct-chart2', {series: [{name: 'series1',data: series_to_plot}]},
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
        $('#' + selector_id).select2();
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
        label.innerHTML = response.display_names[response.actual_names[i]]
    }
}

$('#select').on('change', function() {
  var file_name = $('#select').children("option:selected").val();
  $.getJSON('/load_load/' + file_name, plot_load)
  $.getJSON('/demo_options/' + file_name, add_demo_selectors)
});
