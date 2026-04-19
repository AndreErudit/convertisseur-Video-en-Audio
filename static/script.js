function convert() {
    let fileInput = document.getElementById("fileInput");
    let progressBar = document.getElementById("progressBar");
    let status = document.getElementById("status");

    if (fileInput.files.length === 0) {
        status.textContent = "Choisis un fichier.";
        return;
    }

    let file = fileInput.files[0];

    if (file.size > 60 * 1024 * 1024) {
        status.textContent = "❌ Max 60MB";
        return;
    }

    let xhr = new XMLHttpRequest();
    let formData = new FormData();
    formData.append("file", file);

    xhr.open("POST", "/convert", true);

    xhr.upload.onprogress = function(e) {
        if (e.lengthComputable) {
            let percent = (e.loaded / e.total) * 100;
            progressBar.style.width = percent + "%";
        }
    };

    xhr.onload = function() {
        if (xhr.status === 200) {
            let blob = xhr.response;
            let url = window.URL.createObjectURL(blob);

            let a = document.createElement("a");
            a.href = url;
            a.download = "audio.mp3";
            a.click();

            status.textContent = "✅ Terminé";
        } else {
            status.textContent = "❌ Erreur";
        }
    };

    xhr.responseType = "blob";
    xhr.send(formData);

    status.textContent = "⏳ Upload...";
}