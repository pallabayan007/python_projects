
$(document).ready(function() {
    var dropdown = document.getElementById('client-dropdown')

    var defaultOption = document.createElement('option')
    defaultOption.text = '- choose -'
    defaultOption.value = 'choose'

    dropdown.add(defaultOption);

    var option

    for(client in clients) {
        option = document.createElement('option')
        option.text = clients[client]
        option.value = clients[client]
        dropdown.add(option)
    }
})


function selectconfigfile() {

    var configfile = document.getElementById("configfile")
    var txt = "";

    var allowedExtensions = /(\.ini)$/i;

    if ('files' in configfile) {
        if (configfile.files.length == 0) {
            alert("Select one file");
        } else if (configfile.files.length > 1) {
            alert("Select only one file")
            configfile.value = ""
        } else {
            if (!allowedExtensions.exec(configfile.value)) {
                alert("Invalid file type")
                configfile.value = ""
                return false;
            }  else {
                for (var i = 0; i < configfile.files.length; i++) {
                    txt += "<br><strong>" + (i+1) + ". file</strong><br>"
                    var file = configfile.files[i];
                    if ('name' in file) {
                        txt += "name: " + file.name + "<br>"
                    }
                    if ('size' in file) {
                        txt += "size: " + file.size + " bytes <br>"
                    }
                }
            }
        }
    } else {
	    if (configfile.value == "") {
		    txt += "Select one file"
	    } else {
            txt += "The files property is not supported by your browser!"
            txt += "<br>The path of the selected file: " + configfile.value
	    }
	}
    document.getElementById ("filemessage").innerHTML = txt
}


function uploadconfigfile(progress, progressbar) {

    var file = document.getElementById("configfile")
    var filename = ""

    for(var i=0; i<file.files.length; i++) {
		filename = file.files[i].name;
		if(filename.includes("graphconfig")) {
			uploadfile('configfile', progress, progressbar, 'ico_upldtrainingcompleted','ico_upldtrainingfailed');
		}
		else {
			alert("Please select correct file");
		}
	}
}


function uploadfile(filename, progress, progressbar, completeicon, failureicon) {

    var file = document.getElementById(filename)
    var filename = ""

    var files = new FormData()
    var url = "/upload/"

    for(var i=0; i<file.files.length; i++) {

        displayprogressbar(progress, progressbar, 10)

        filename = file.files[i].name
        var filetype=""
        if(filename.includes("config")){
			filetype="config"
		}
		else if(filename.includes("training")){
			filetype="training"
		}

		headers = {'filename': filename, 'filetype':filetype, 'Content-Disposition': 'attachment; filename='+filename}
        $.ajax({
			type: 'post',
			url: url,
			processData: false,
			contentType : '*/*',
			headers: headers,
			data: file.files[i],
			success: function (response) {
			    hideprogressbar(progress)
				if(response.status){
					document.getElementById(completeicon).hidden=false;
				} else {
					document.getElementById(failureicon).hidden=false;
				}
			},
			error: function (err) {
			    hideprogressbar(progress)
				document.getElementById(failureicon).hidden=false;
			}
		})
    }
}


function getPrediction() {

    var dropdown = document.getElementById('client-dropdown')
    if((dropdown.selectedIndex - 1) >=0)
//        window.location.href = '../predict/?client=' + clients[dropdown.selectedIndex - 1]
        window.open('../predict/?client=' + clients[dropdown.selectedIndex - 1])
    else
        alert('Please select a client to proceed');
}


function displayprogressbar(divname, barname, barwaittime) {
	var x = document.getElementById(divname);
	x.hidden = false
	move(barname, barwaittime);
}


function hideprogressbar(divname) {
	var x = document.getElementById(divname);
	x.hidden=true
}


function move(barname, barwaittime) {
    var i = 0;
    if (i == 0) {
	    i = 1
        var elem = document.getElementById(barname)
	    var width = 1
	    var id = setInterval(frame, barwaittime)
        function frame() {
            if (width >= 100) {
                clearInterval(id)
                i = 0
            } else {
                width++
                elem.style.width = width + "%"
            }
        }
    }
}
