
listener = {}

var setup_vertical_resizing_pair = function(active_element_id, compensating_element_id, plot_to_resize){

    parent_height = $(active_element_id).parent().height();
    active_element_id_percentage_height = ($(active_element_id).height()/parent_height) * 100 ;
    compensating_element_id_percentage_height = ($(compensating_element_id).height()/parent_height) * 100;
    console.log(active_element_id_percentage_height)

    delete listener.compensator

    listener.compensator = new ResizeSensor($(active_element_id), function(){
        adjust_heights(active_element_id, active_element_id_percentage_height,
                       compensating_element_id, compensating_element_id_percentage_height,
                       document.getElementById(plot_to_resize));
    });

    var adjust_heights = function(resized_element_id, orginal_percentage_height, compensating_element_id,
                                  comp_element_original_percemtage, graph_to_update){
        var resized_element_height = $(resized_element_id).height();
        var parent_element_height = $(resized_element_id).parent().height();
        var original_height = parent_element_height * (orginal_percentage_height / 100);
        var height_change = resized_element_height - original_height;
        var compensating_element_orinal_height = parent_element_height * (comp_element_original_percemtage / 100);
        var compensating_element_new_height = compensating_element_orinal_height -  height_change;
        $(compensating_element_id).height(compensating_element_new_height)
        Plotly.Plots.resize(graph_to_update)
    }

    window.onresize = function(event) {
        $(active_element_id).css('height', active_element_id_percentage_height.toString() + '%');
        $(compensating_element_id).css('height', compensating_element_id_percentage_height.toString() + '%');
    };


};
