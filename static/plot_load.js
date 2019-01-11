$('#select').on('change', function() {
  var file_name = $('#select').children("option:selected").val();
  $.getJSON('/load_load/' + file_name, function(response){
    // Create a new line chart object where as first parameter we pass in a selector
    // that is resolving to our chart container element. The Second parameter
    // is the actual data object.
    console.log(response);

    var series_to_plot = [];
    var arraylength = response.Time.length
    for (var i = 0; i < arraylength; i++){
        var date_time = response.Time[i]
        var date = date_time.split(' ')[0]
        var time = date_time.split(' ')[1]
        var year = date.split('-')[0]
        var month = date.split('-')[1]
        var day = date.split('-')[2]
        var hour = time.split(':')[0]

        var minute = time.split(':')[1]
        var second = time.split(':')[2]
        var date_time_obj = new Date(year, (month - 1), day, hour, minute, second)
        series_to_plot.push({x: date_time_obj, y: response.Mean[i]})
    }
    var chart = new Chartist.Line('.ct-chart2', {series: [{name: 'series1',data: series_to_plot}]},
      {axisX: { type: Chartist.FixedScaleAxis, divisor: 5, labelInterpolationFnc: function(value) {
          return moment(value).format('MMM D '); }}, showPoint: false, lineSmoothed: false}
      );
  })
});
