var add_demo_selectors = function(response){
    console.log(response)
    var arraylength = response.actual_names.length

    for (var i = 0; i < 10; i++){
        selector_id = "demo_select_" + i.toString()
        div_id = "demo_" + i.toString()
        label_id = "demo_label_" + i.toString()
        var label = document.getElementById(label_id);
        $('#'+div_id).hide()
        $('#'+selector_id).find('option').remove()
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

var get_load_details_from_ui = function(){

    var filter_options = {}

    for (var i = 0; i < 10; i++){
        selector_id = "demo_select_" + i.toString()
        label_id = "demo_label_" + i.toString()
        var label = document.getElementById(label_id);
        var values = $('#' + selector_id).val();
        if (label.innerHTML !== ''){
                filter_options[label.innerHTML] = values;
                }
    }

    var file_name = $('#select').children("option:selected").val();

    var chart_type = $('#select_graph').children("option:selected").val();

    var load_request = {'file_name': file_name, 'filter_options': filter_options, 'chart_type': chart_type}

    return load_request

}

var plot_filtered_load =  function(){

    load_request = get_load_details_from_ui()

    $.ajax({
    url: '/filtered_load_data',
    data: JSON.stringify(load_request),
    contentType: 'application/json;charset=UTF-8',
    type : 'POST',
    async: 'false',
    dataType:"json",
    success: function(data, n_users){
    plot_load(data);}
    });

}

var plot_load = function(response){
    var layout = {margin: { l: 40, r: 35, b: 40, t: 20, pad: 0 },
                  paper_bgcolor: '#EEEEEE',
                  plot_bgcolor: '#c7c7c7',
                  showlegend: true};
    Plotly.newPlot('load_chart', response['chart_data'], layout, {responsive: true});
    var file_name = $('#select').children("option:selected").val();
    print_n_users(response['n_users'])
    //$('#get_load').contextMenu('close');
    $('#dialog').dialog('close');
}

var print_n_users = function(n_users){
    console.log(n_users)
    var label = document.getElementById('sample_size_info');
    label.innerHTML = 'No. of users: ' + n_users ;
}

var make_loading_popup = function(){
  let params = `scrollbars=no, resizable=no, status=no, location=no, toolbar=no, menubar=no,
  width=300,height=50,left=500,top=500`;
  let newWindow = open(',', 'example', params)
  newWindow.focus();

  newWindow.onload = function() {
    let html = `<div style="font-size:20px, background-color: #EEEEEE; text-align: center;">Please Wait! Loading data.</div>`;
    newWindow.document.write(html);
  };
  return newWindow
}

var perform_plot_load_actions = function(){
    $('#dialog').dialog({modal: true});
    var file_name = $('#select').children("option:selected").val();
    $.getJSON('/demo_options/' + file_name, add_demo_selectors);
    plot_filtered_load();
}

$('#select').on('change', function() {
    perform_plot_load_actions();
});

$('.select_demo').on('change', function() {
    $('#dialog').dialog({modal: true});
    plot_filtered_load();
});

$('#select_graph').on('change', function() {
    $('#dialog').dialog({modal: true});
    plot_filtered_load();
});

window.onresize = function() {
    Plotly.Plots.resize('load_chart');
};

