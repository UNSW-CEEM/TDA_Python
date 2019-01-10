$('#select').on('change', function() {
  var file_name = $('#select').children("option:selected").val();
  $.getJSON('/load_load/' + file_name, function(response){
    // Create a new line chart object where as first parameter we pass in a selector
    // that is resolving to our chart container element. The Second parameter
    // is the actual data object.
    console.log(response);
    new Chartist.Line('.ct-chart2', {labels: response.Time, series: [response.Mean]});
  })
});
