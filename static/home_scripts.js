function upload() {
    var fileInput = document.getElementById('file_input')
    fileInput.addEventListener('change', handleFileUpload) 
    fileInput.click()
}

function switchView(view) {}

function handleFileUpload(e) {
    var files = e.target.files;
    
    if (files.length === 0) { return; }

    var form = new FormData();

    for (var i = 0; i < files.length; i++) {
        form.append('files', files[i]);
        form.append('modifieds', files[i].lastModified);
    }

    document.getElementById('upload').innerHTML = 'Files uploading...';

    fetch('/upload', {
        method: 'POST',
        body: form
    })
        .then(response => response.text())
        .then(text => document.getElementById('upload').innerHTML = text);
}