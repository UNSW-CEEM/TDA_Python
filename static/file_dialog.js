
var get_file_and_pass_to_python = function(extension, url, call_back){

    $('#file1').on('change', function(){
        var xhr = new XMLHttpRequest();
        xhr.open("POST", url);
        xhr.onload = function(event){
             call_back(JSON.parse(event.target.response)); // raw response
        };
        // or onerror, onabort
        var formData = new FormData(document.getElementById("file_form"));
        xhr.send(formData);
    })

    $('#file1').prop('accept', extension);
    $('#file1').click();
}

