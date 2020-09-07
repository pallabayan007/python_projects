
$(document).ready(function() {
    var container = document.getElementById("graphs")

    for (var d in data) {
        if(d!='client') {
            console.log(data[d])
            var img = document.createElement("img")
            img.src = "data:image/png;base64,"+data[d]
            img.alt = ""
            img.height = "600"
            img.width = "1000"
            container.appendChild(img)
        }
    }
})
