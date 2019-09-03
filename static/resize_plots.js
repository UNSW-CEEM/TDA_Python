
var window_resize_events = []

var setup_vertical_resizing_pair = function(active_element_id, compensating_element_id, plot_to_resize, listener){

    parent_height = $(active_element_id).parent().height();
    active_element_id_percentage_height = ($(active_element_id).height()/parent_height) * 100 ;
    compensating_element_id_percentage_height = ($(compensating_element_id).height()/parent_height) * 100;
    console.log(active_element_id_percentage_height)

    listener.div = function(re_element_id, orig_percentage_height, comp_element_id,
                                  comp_element_original_percentage, graph_to_update){

        return function(){
            var resized_element_height = $(re_element_id).height();
            var parent_element_height = $(re_element_id).parent().height();
            var original_height = parent_element_height * (orig_percentage_height / 100);
            var height_change = resized_element_height - original_height;
            var compensating_element_original_height = parent_element_height * (comp_element_original_percentage / 100);
            var compensating_element_new_height = compensating_element_original_height -  height_change;
            $(comp_element_id).height(compensating_element_new_height)
            if (graph_to_update != 'none'){
                Plotly.Plots.resize(document.getElementById(graph_to_update))
            }
        }

    }(active_element_id, active_element_id_percentage_height, compensating_element_id,
    compensating_element_id_percentage_height, plot_to_resize)

    new ResizeSensor($(active_element_id), function(){
        listener.div();
    });

    listener.window = function(re_element_id, orig_percentage_height, comp_element_id,
                              comp_element_original_percentage){
        return function(){
           $(re_element_id).css('height', orig_percentage_height.toString() + '%');
           $(comp_element_id).css('height', comp_element_original_percentage.toString() + '%');
           }
    }(active_element_id, active_element_id_percentage_height, compensating_element_id,
      compensating_element_id_percentage_height);

    window_resize_events.push(listener.window);

};

var wholesale_listener = {'div': '', 'window':''}
setup_vertical_resizing_pair('#wholesale_price_selection', '#price_inspection', 'price_chart', wholesale_listener);
var load_listener = {'div': '', 'window':''}
setup_vertical_resizing_pair('#load_selection', '#load_inspection', 'load_chart', load_listener);
var tech_listener = {'div': '', 'window':''}
setup_vertical_resizing_pair('#end_user_tech_inputs', '#net_load_inspection', 'none', tech_listener);
var network_listener = {'div': '', 'window':''}
setup_vertical_resizing_pair('#network_tariff_selection_panel .upper_tariff_section',
                             '#network_tariff_selection_panel .lower_tariff_section', 'none', network_listener);
var retail_listener = {'div': '', 'window':''}
setup_vertical_resizing_pair('#retail_tariff_selection_panel .upper_tariff_section',
                             '#retail_tariff_selection_panel .lower_tariff_section', 'none', retail_listener);

window.onresize = function(event){
      for (i = 0; i < window_resize_events.length; i++) {
      window_resize_events[i]();
  }
}