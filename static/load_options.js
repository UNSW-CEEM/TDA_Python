console.log('Hi im');
// This is a jquery function that visits the '/data' endpoint. See run.py  (or try in your browser)
$.getJSON('/load_names', function(response){

    // printing the response from the server when the program visits localhost:5000/data
    console.log('Hi');
    console.log(response);

    // This is the 
    var names = {response};

    // Create a new line chart object where as first parameter we pass in a selector
    // that is resolving to our chart container element. The Second parameter
    // is the actual data object.
    new ('.ct-chart', data);
})



