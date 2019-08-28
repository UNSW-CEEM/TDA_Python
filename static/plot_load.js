var add_demo_selectors = function(response){
    var arraylength = response.actual_names.length

    // Hide existing selectors and remove content
    for (var i = 0; i < 10; i++){
        selector_id = "demo_select_" + i.toString()
        div_id = "demo_" + i.toString()
        label_id = "demo_label_" + i.toString()
        var label = document.getElementById(label_id);
        $('#'+div_id).hide()
        $('#'+selector_id).find('option').remove()
        label.innerHTML = ''
    }

    // Show the required selectors and add the new content to them.
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

var get_down_sample_setting = function(){
    var chosen_down_sample_option
    var options = $('.down_sample_option')
    $.each(options, function(i, option){
        if ($(option).is(":checked")){
            chosen_down_sample_option = parseFloat($(option).attr('value'))
        }
    });
    return chosen_down_sample_option
}

var get_missing_data_limit = function(){
    var chosen_missing_data_limit
    var options = $('.missing_data_limit')
    $.each(options, function(i, option){
        if ($(option).is(":checked")){
            chosen_missing_data_limit = parseFloat($(option).attr('value'))
        }
    });
    return chosen_missing_data_limit
}

var get_network_load_setting = function(){
    // Check which network load type is checked in the drop down menu.
    var chosen_network_load
    var options = $('.network_load_option')
    $.each(options, function(i, option){
        if ($(option).is(":checked")){
            chosen_network_load = $(option).attr('value')
        }
    });

    // If the synthetic option is chosen then replace the return value with the name of the chosen synthetic load.
    if (chosen_network_load == 'synthetic'){
         var synthetic_options = $('.synthetic_network_load_option')
        $.each(synthetic_options, function(i, option){
            if ($(option).is(":checked")){
                chosen_network_load = $(option).attr('value')
            }
        });
    }

    console.log(chosen_network_load)
    return chosen_network_load
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

    var down_sample_option = get_down_sample_setting();

    var missing_data_limit = get_missing_data_limit();

    var network_load = get_network_load_setting();

    var load_request = {'file_name': file_name, 'filter_options': filter_options, 'chart_type': chart_type,
                        'sample_fraction': down_sample_option, 'missing_data_limit': missing_data_limit,
                        'network_load': network_load};

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

    console.log("response:",response);
    console.log("response[layout]:",response['chart_data']['layout']);
    var layout = {autosize: true,
                  margin: { l: 40, r: 35, b: 40, t: 20, pad: 0 },
                  paper_bgcolor: '#EEEEEE',
                  plot_bgcolor: '#c7c7c7',
                  showlegend: false,
                  xaxis: response['chart_data']['layout'].xaxis,
                  yaxis: response['chart_data']['layout'].yaxis};

    Plotly.newPlot('load_chart', response['chart_data']['data'], layout);
    var file_name = $('#select').children("option:selected").val();
    print_n_users(response['n_users'])
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
    $.getJSON('/get_demo_options/' + file_name, add_demo_selectors);
    plot_filtered_load();
}

$('#select').on('change', function() {
    perform_plot_load_actions();
});

$('.down_sample_option').on('change', function() {
    perform_plot_load_actions();
});

$('.missing_data_limit').on('change', function() {
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

