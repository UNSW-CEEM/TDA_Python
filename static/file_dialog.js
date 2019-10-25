
var get_file_and_pass_to_python = function(extension, url, call_back){

    $('#file1').on('change', function(){
        var xhr = new XMLHttpRequest();
        xhr.open("POST", url);
        xhr.onload = function(event){
            var json_data = JSON.parse(event.target.response);
            alert_user_if_error(json_data);
            call_back(json_data);
        };
        // or onerror, onabort
        var formData = new FormData(document.getElementById("file_form"));
        xhr.send(formData);
    })

    $('#file1').prop('accept', extension);
    $('#file1').click();
}

var get_file_from_python_and_save_to_disk = function(extension, url, call_back){

    $.ajax({
        url: url,
        data: JSON.stringify(request_details),
        contentType: 'application/json;',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            download('new_project', data)
        }
    });

}

var download = function(filename, text) {
    console.log('Downloading!')
    var pom = document.createElement('a');
    pom.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    pom.setAttribute('download', filename);
    if (document.createEvent) {
        var event = document.createEvent('MouseEvents');
        event.initEvent('click', true, true);
        pom.dispatchEvent(event);
    } else {
        pom.click();
    }
}