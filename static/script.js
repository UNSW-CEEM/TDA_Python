
// THis is javascript's 'print' function - you can open up your js console in your browser and see them.
console.log('Hi im javascript');


// This is a jquery function that visits the '/data' endpoint. See run.py  (or try in your browser)
$.getJSON('/data',function(response){

    // printing the response from the server when the program visits localhost:5000/data
    console.log(response);

    // This is the 
    var data = {
        // A labels array that can contain any sort of values
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
        // Our series array that contains series objects or in this case series data arrays
        series: [
            response.data
            // [5, 2, 4, 2, 0]
        ]
    };

    // Create a new line chart object where as first parameter we pass in a selector
    // that is resolving to our chart container element. The Second parameter
    // is the actual data object.
    new Chartist.Line('.ct-chart', data);
})

