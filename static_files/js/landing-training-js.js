
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


function selecttrainingfiles() {

    var trainingfiles = document.getElementById("trainingfiles")
    var txt = "";

    var allowedExtensions = /(\.csv)$/i;

    if ('files' in trainingfiles) {
        if (trainingfiles.files.length == 0) {
            alert("Select one or more files")
        } else {
            if (!allowedExtensions.exec(trainingfiles.value)) {
                alert("Invalid file type");
                trainingfiles.value = "";
                return false;
            }  else {
                for (var i = 0; i < trainingfiles.files.length; i++) {
                    txt += "<br><strong>" + (i+1) + ". file</strong><br>"
                    var file = trainingfiles.files[i];
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
	    if (trainingfiles.value == "") {
		    txt += "Select one or more files"
	    } else {
            txt += "The files property is not supported by your browser!"
            txt += "<br>The path of the selected file: " + trainingfiles.value
	    }
	}
    document.getElementById ("trainingfilemessage").innerHTML = txt
}


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
    document.getElementById ("configfilemessage").innerHTML = txt
}


function uploadfile(filetype, progress, progressbar, completeicon, failureicon) {

    var file = document.getElementById(filetype)
    var filename = ""

    for(var i=0; i<file.files.length; i++) {
		filename = file.files[i].name;
		if(filename.includes("dataconfig") || filename.includes("training")) {
			upload(filetype, progress, progressbar, completeicon, failureicon);
		}
		else {
			alert("Please select correct file");
		}
	}
}


function upload(filename, progress, progressbar, completeicon, failureicon) {

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


function getTraining(progress, progressbar) {

    var dropdown = document.getElementById('client-dropdown')
    var txt = ""

    if((dropdown.selectedIndex - 1) >=0) {
        url = "/train/?client=" + clients[dropdown.selectedIndex - 1]

        displayprogressbar(progress, progressbar, 10)

        $.ajax({
			type: 'get',
			url: url,
			processData: false,
			success: function (response) {
			    hideprogressbar(progress)
				if(response.status) {
					document.getElementById ("trainingmessage").innerHTML = "Trained successfully"
				} else {
					document.getElementById ("trainingmessage").innerHTML = "Training unsuccessful"
				}
			},
			error: function (err) {
			    hideprogressbar(progress)
				document.getElementById ("trainingmessage").innerHTML = "Training unsuccessful"
			}
		})
	} else
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