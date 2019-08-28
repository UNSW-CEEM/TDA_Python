new ResizeSensor(document.getElementById('load_selection'), function(){
    adjust_heights('#load_selection', 60, '#load_inspection', 38, '#load_con',
                   document.getElementById('load_chart'));
});

var adjust_heights = function(resized_element_id, orginal_percentage_height, compensating_element_id,
                              comp_element_original_percemtage, parent_id, graph_to_update){
    var resized_element_height = $(resized_element_id).height();
    var parent_element_height = $(parent_id).height();
    var original_height = parent_element_height * (orginal_percentage_height / 100);
    var height_change = resized_element_height - original_height;
    var compensating_element_orinal_height = parent_element_height * (comp_element_original_percemtage / 100);
    var compensating_element_new_height = compensating_element_orinal_height -  height_change;
    $(compensating_element_id).height(compensating_element_new_height)
    Plotly.Plots.resize(graph_to_update)
}

window.onresize = function(event) {
    $('#load_selection').css('height', '60%');
    $('#load_inspection').css('height', '38%');
};