/* NUGET: BEGIN LICENSE TEXT
 *
 * Microsoft grants you the right to use these script files for the sole
 * purpose of either: (i) interacting through your browser with the Microsoft
 * website or online service, subject to the applicable licensing or use
 * terms; or (ii) using the files as included with a Microsoft product subject
 * to that product's license terms. Microsoft reserves all other rights to the
 * files not expressly granted by Microsoft, whether by implication, estoppel
 * or otherwise. Insofar as a script file is dual licensed under GPL,
 * Microsoft neither took the code under GPL nor distributes it thereunder but
 * under the terms set out in this paragraph. All notices and licenses
 * below are for informational purposes only.
 *
 * NUGET: END LICENSE TEXT */
/*! matchMedia() polyfill - Test a CSS media type/query in JS. Authors & copyright (c) 2012: Scott Jehl, Paul Irish, Nicholas Zakas. Dual MIT/BSD license */
/*! NOTE: If you're already including a window.matchMedia polyfill via Modernizr or otherwise, you don't need this part */
window.matchMedia = window.matchMedia || (function(doc, undefined){
  
  var bool,
      docElem  = doc.documentElement,
      refNode  = docElem.firstElementChild || docElem.firstChild,
      // fakeBody required for <FF4 when executed in <head>
      fakeBody = doc.createElement('body'),
      div      = doc.createElement('div');
  
  div.id = 'mq-test-1';
  div.style.cssText = "position:absolute;top:-100em";
  fakeBody.style.background = "none";
  fakeBody.appendChild(div);
  
  return function(q){
    
    div.innerHTML = '&shy;<style media="'+q+'"> #mq-test-1 { width: 42px; }</style>';
    
    docElem.insertBefore(fakeBody, refNode);
    bool = div.offsetWidth == 42;  
    docElem.removeChild(fakeBody);
    
    return { matches: bool, media: q };
  };
  
})(document);




/*! Respond.js v1.2.0: min/max-width media query polyfill. (c) Scott Jehl. MIT/GPLv2 Lic. j.mp/respondjs  */
(function( win ){
	//exposed namespace
	win.respond		= {};
	
	//define update even in native-mq-supporting browsers, to avoid errors
	respond.update	= function(){};
	
	//expose media query support flag for external use
	respond.mediaQueriesSupported	= win.matchMedia && win.matchMedia( "only all" ).matches;
	
	//if media queries are supported, exit here
	if( respond.mediaQueriesSupported ){ return; }
	
	//define vars
	var doc 			= win.document,
		docElem 		= doc.documentElement,
		mediastyles		= [],
		rules			= [],
		appendedEls 	= [],
		parsedSheets 	= {},
		resizeThrottle	= 30,
		head 			= doc.getElementsByTagName( "head" )[0] || docElem,
		base			= doc.getElementsByTagName( "base" )[0],
		links			= head.getElementsByTagName( "link" ),
		requestQueue	= [],
		
		//loop stylesheets, send text content to translate
		ripCSS			= function(){
			var sheets 	= links,
				sl 		= sheets.length,
				i		= 0,
				//vars for loop:
				sheet, href, media, isCSS;

			for( ; i < sl; i++ ){
				sheet	= sheets[ i ],
				href	= sheet.href,
				media	= sheet.media,
				isCSS	= sheet.rel && sheet.rel.toLowerCase() === "stylesheet";

				//only links plz and prevent re-parsing
				if( !!href && isCSS && !parsedSheets[ href ] ){
					// selectivizr exposes css through the rawCssText expando
					if (sheet.styleSheet && sheet.styleSheet.rawCssText) {
						translate( sheet.styleSheet.rawCssText, href, media );
						parsedSheets[ href ] = true;
					} else {
						if( (!/^([a-zA-Z:]*\/\/)/.test( href ) && !base)
							|| href.replace( RegExp.$1, "" ).split( "/" )[0] === win.location.host ){
							requestQueue.push( {
								href: href,
								media: media
							} );
						}
					}
				}
			}
			makeRequests();
		},
		
		//recurse through request queue, get css text
		makeRequests	= function(){
			if( requestQueue.length ){
				var thisRequest = requestQueue.shift();
				
				ajax( thisRequest.href, function( styles ){
					translate( styles, thisRequest.href, thisRequest.media );
					parsedSheets[ thisRequest.href ] = true;
					makeRequests();
				} );
			}
		},
		
		//find media blocks in css text, convert to style blocks
		translate			= function( styles, href, media ){
			var qs			= styles.match(  /@media[^\{]+\{([^\{\}]*\{[^\}\{]*\})+/gi ),
				ql			= qs && qs.length || 0,
				//try to get CSS path
				href		= href.substring( 0, href.lastIndexOf( "/" )),
				repUrls		= function( css ){
					return css.replace( /(url\()['"]?([^\/\)'"][^:\)'"]+)['"]?(\))/g, "$1" + href + "$2$3" );
				},
				useMedia	= !ql && media,
				//vars used in loop
				i			= 0,
				j, fullq, thisq, eachq, eql;

			//if path exists, tack on trailing slash
			if( href.length ){ href += "/"; }	
				
			//if no internal queries exist, but media attr does, use that	
			//note: this currently lacks support for situations where a media attr is specified on a link AND
				//its associated stylesheet has internal CSS media queries.
				//In those cases, the media attribute will currently be ignored.
			if( useMedia ){
				ql = 1;
			}
			

			for( ; i < ql; i++ ){
				j	= 0;
				
				//media attr
				if( useMedia ){
					fullq = media;
					rules.push( repUrls( styles ) );
				}
				//parse for styles
				else{
					fullq	= qs[ i ].match( /@media *([^\{]+)\{([\S\s]+?)$/ ) && RegExp.$1;
					rules.push( RegExp.$2 && repUrls( RegExp.$2 ) );
				}
				
				eachq	= fullq.split( "," );
				eql		= eachq.length;
					
				for( ; j < eql; j++ ){
					thisq	= eachq[ j ];
					mediastyles.push( { 
						media	: thisq.split( "(" )[ 0 ].match( /(only\s+)?([a-zA-Z]+)\s?/ ) && RegExp.$2 || "all",
						rules	: rules.length - 1,
						hasquery: thisq.indexOf("(") > -1,
						minw	: thisq.match( /\(min\-width:[\s]*([\s]*[0-9\.]+)(px|em)[\s]*\)/ ) && parseFloat( RegExp.$1 ) + ( RegExp.$2 || "" ), 
						maxw	: thisq.match( /\(max\-width:[\s]*([\s]*[0-9\.]+)(px|em)[\s]*\)/ ) && parseFloat( RegExp.$1 ) + ( RegExp.$2 || "" )
					} );
				}	
			}

			applyMedia();
		},
        	
		lastCall,
		
		resizeDefer,
		
		// returns the value of 1em in pixels
		getEmValue		= function() {
			var ret,
				div = doc.createElement('div'),
				body = doc.body,
				fakeUsed = false;
									
			div.style.cssText = "position:absolute;font-size:1em;width:1em";
					
			if( !body ){
				body = fakeUsed = doc.createElement( "body" );
				body.style.background = "none";
			}
					
			body.appendChild( div );
								
			docElem.insertBefore( body, docElem.firstChild );
								
			ret = div.offsetWidth;
								
			if( fakeUsed ){
				docElem.removeChild( body );
			}
			else {
				body.removeChild( div );
			}
			
			//also update eminpx before returning
			ret = eminpx = parseFloat(ret);
								
			return ret;
		},
		
		//cached container for 1em value, populated the first time it's needed 
		eminpx,
		
		//enable/disable styles
		applyMedia			= function( fromResize ){
			var name		= "clientWidth",
				docElemProp	= docElem[ name ],
				currWidth 	= doc.compatMode === "CSS1Compat" && docElemProp || doc.body[ name ] || docElemProp,
				styleBlocks	= {},
				lastLink	= links[ links.length-1 ],
				now 		= (new Date()).getTime();

			//throttle resize calls	
			if( fromResize && lastCall && now - lastCall < resizeThrottle ){
				clearTimeout( resizeDefer );
				resizeDefer = setTimeout( applyMedia, resizeThrottle );
				return;
			}
			else {
				lastCall	= now;
			}
										
			for( var i in mediastyles ){
				var thisstyle = mediastyles[ i ],
					min = thisstyle.minw,
					max = thisstyle.maxw,
					minnull = min === null,
					maxnull = max === null,
					em = "em";
				
				if( !!min ){
					min = parseFloat( min ) * ( min.indexOf( em ) > -1 ? ( eminpx || getEmValue() ) : 1 );
				}
				if( !!max ){
					max = parseFloat( max ) * ( max.indexOf( em ) > -1 ? ( eminpx || getEmValue() ) : 1 );
				}
				
				// if there's no media query at all (the () part), or min or max is not null, and if either is present, they're true
				if( !thisstyle.hasquery || ( !minnull || !maxnull ) && ( minnull || currWidth >= min ) && ( maxnull || currWidth <= max ) ){
						if( !styleBlocks[ thisstyle.media ] ){
							styleBlocks[ thisstyle.media ] = [];
						}
						styleBlocks[ thisstyle.media ].push( rules[ thisstyle.rules ] );
				}
			}
			
			//remove any existing respond style element(s)
			for( var i in appendedEls ){
				if( appendedEls[ i ] && appendedEls[ i ].parentNode === head ){
					head.removeChild( appendedEls[ i ] );
				}
			}
			
			//inject active styles, grouped by media type
			for( var i in styleBlocks ){
				var ss		= doc.createElement( "style" ),
					css		= styleBlocks[ i ].join( "\n" );
				
				ss.type = "text/css";	
				ss.media	= i;
				
				//originally, ss was appended to a documentFragment and sheets were appended in bulk.
				//this caused crashes in IE in a number of circumstances, such as when the HTML element had a bg image set, so appending beforehand seems best. Thanks to @dvelyk for the initial research on this one!
				head.insertBefore( ss, lastLink.nextSibling );
				
				if ( ss.styleSheet ){ 
		        	ss.styleSheet.cssText = css;
		        } 
		        else {
					ss.appendChild( doc.createTextNode( css ) );
		        }
		        
				//push to appendedEls to track for later removal
				appendedEls.push( ss );
			}
		},
		//tweaked Ajax functions from Quirksmode
		ajax = function( url, callback ) {
			var req = xmlHttp();
			if (!req){
				return;
			}	
			req.open( "GET", url, true );
			req.onreadystatechange = function () {
				if ( req.readyState != 4 || req.status != 200 && req.status != 304 ){
					return;
				}
				callback( req.responseText );
			}
			if ( req.readyState == 4 ){
				return;
			}
			req.send( null );
		},
		//define ajax obj 
		xmlHttp = (function() {
			var xmlhttpmethod = false;	
			try {
				xmlhttpmethod = new XMLHttpRequest();
			}
			catch( e ){
				xmlhttpmethod = new ActiveXObject( "Microsoft.XMLHTTP" );
			}
			return function(){
				return xmlhttpmethod;
			};
		})();
	
	//translate CSS
	ripCSS();
	
	//expose update for re-running respond later on
	respond.update = ripCSS;
	
	//adjust on resize
	function callMedia(){
		applyMedia( true );
	}
	if( win.addEventListener ){
		win.addEventListener( "resize", callMedia, false );
	}
	else if( win.attachEvent ){
		win.attachEvent( "onresize", callMedia );
	}
})(this);


// var input = document.getElementById("Log_in");
// input.addEventListener("keyup", function(event) {
//     if (event.keyCode === 13) {
//         event.preventDefault();
//         document.getElementById("Log_in").click();
//     }
// });

function weathergraph() {
//   var xhttp = new XMLHttpRequest();
// //   alert(username);
// //   alert("hi");
//   xhttp.onreadystatechange = function() {
//     if (this.readyState == 4 && this.status == 200) {
//     //   document.getElementById("demo").innerHTML =
// 	//   this.responseText;
// 		// alert(username);
//     }
//   };
//   	xhttp.open("GET", "http://127.0.0.1:8000/weather/", true);
// 	xhttp.send(); 
	
	// $('#weathergraph').on('submit',function(e){
	// 	e.preventDefault();
	// 	$.get('/weather/',
	// 		  function(response){ $('#response_msg').text(response.msg);}
	// 	);
	// });  
}
// Calling the training system
$(document).ready(function () {  
	$("#runtraining").click(function () { 
		document.getElementById("ico_completed").hidden=true;
		document.getElementById("ico_failed").hidden=true;
		document.querySelector(('#trainingdiv #runtrainingstatusmsg')).hidden=false;
		document.querySelector(('#trainingdiv #runtrainingstatusmsg')).innerHTML="";
		let dropdown = document.getElementById('client-dropdown');
		console.log("++++++++++++inside run training:");
		console.log("++++++++++++inside dropdown:" + dropdown.value);
		console.log(dropdown.value === "");

		if (dropdown.value!=="choose" && dropdown.value !== "" && dropdown.value!= null) {
			console.log("++++++++++++inside iff:");
			senddata = '{"client":"' + dropdown.value + '"}'
			senddata_json= JSON.parse(senddata)
			console.log("++++senddata================== " + senddata)
			displayprogressbar("myProgress","myBar",50);		
			$.post('/api/training',senddata, function (data, status) {  
				console.log("++++++++++++training response:" + data);
				console.log("++++++++++++typeof:" + typeof data);
				console.log("++++++++++++typeof:" + typeof "true");
				console.log("++++++++++++data == True:" + (data == "True"));
				hideprogressbar("myProgress");
				if(data == "True"){
					document.getElementById("ico_completed").hidden=false;
				} 
				else{
					document.getElementById("ico_failed").hidden=false;
					errormsg = "There is a problem in server training, please try again later";
					document.querySelector(('#trainingdiv #runtrainingstatusmsg')).hidden=false;
					document.querySelector(('#trainingdiv #runtrainingstatusmsg')).innerHTML=errormsg;
				}
				if(status == "error"){
					console.log("====Inside jquery error++++++")
					hideprogressbar("myProgress");	
					document.getElementById("ico_failed").hidden=false;
				}				
			});  
			
		} else {
			console.log("++++++++++++inside elseee:");
			errormsg = "Please select a client to proceed";
			document.querySelector(('#trainingdiv #runtrainingstatusmsg')).hidden=false;
			document.querySelector(('#trainingdiv #runtrainingstatusmsg')).innerHTML=errormsg;
		}
		
		
	});  
});  

// showing the error msg in case run training encounters bad request
$( document ).ajaxError(function() {
	hideprogressbar("myProgress");	
	document.getElementById("ico_failed").hidden=false;
	errormsg = "There is a problem while running the training, make sure your training data is not erronous";
	
	document.querySelector(('#trainingdiv #runtrainingstatusmsg')).hidden=false;
	document.querySelector(('#trainingdiv #runtrainingstatusmsg')).innerHTML=errormsg;
  });

var i = 0;
function move(barname, barwaittime) {
  if (i == 0) {
	i = 1;
	console.log("=============barname========:" + barname+":"+barwaittime)
    var elem = document.getElementById(barname);
	var width = 1;
	console.log("=============barwaittime========:" + barwaittime)
	var id = setInterval(frame, barwaittime);
	console.log("=============id========:" + id)
    function frame() {
      if (width >= 100) {
        clearInterval(id);
        i = 0;
      } else {
        width++;
        elem.style.width = width + "%";
      }
    }
  }
}

function displayprogressbar(divname,barname,barwaittime) {
	console.log("============Inside displayprogressbar========" + divname+":"+barname+":"+barwaittime)
	var x = document.getElementById(divname);
	x.hidden=false
	move(barname,barwaittime);
	// if (x.style.display === "none") {
	//   x.style.display = "block";
	// } else {
	//   x.style.display = "none";
	// }
  }
  function hideprogressbar(divname) {
	console.log("============Inside hideprogressbar========")
	var x = document.getElementById(divname);
	x.hidden=true
  }
  
//For selecting files to upload
  function selectuploadfile(inputid,paraid){
	var x = document.getElementById(inputid);
	// x.value = "";
	var txt = "";
	if ('files' in x) {
	  if (x.files.length == 0) {
		txt = "Select one or more files.";
	  } else {
		for (var i = 0; i < x.files.length; i++) {
		  txt += "<br><strong>" + (i+1) + ". file</strong><br>";
		  var file = x.files[i];
		  if ('name' in file) {
			txt += "name: " + file.name + "<br>";
		  }
		  if ('size' in file) {
			txt += "size: " + file.size + " bytes <br>";
		  }
		}
	  }
	} 
	else {
	  if (x.value == "") {
		txt += "Select one or more files.";
	  } else {
		txt += "The files property is not supported by your browser!";
		txt  += "<br>The path of the selected file: " + x.value; // If the browser does not support the files property, it will return the path of the selected file instead. 
	  }
	}
	document.getElementById(paraid).innerHTML = txt;
  }

//Uploading intent file on button submission
$('#process-file-button').on('click', function (e) {
	var fileInput = document.getElementById("myFile"); 
	var filename = "";
	for(var i=0; i<fileInput.files.length; i++){
		filename = fileInput.files[i].name;
		console.log("================myfile filename==== " + filename)
		if(filename.includes("intents")){
			uploadfile('myFile','myProgress_upldtrainingdata','myBar_upldtrainingdata','ico_upldtrainingcompleted','ico_upldtrainingfailed');
		}
		else{
			alert("Please select correct file");
		}
	}

	document.getElementById("myFile").value="";
	document.getElementById("demo").innerHTML ="";
  
});

//Uploading config file on button submission
$('#process-file-button1').on('click', function (e) {
	var fileInput = document.getElementById("myFile1"); 
	var filename = "";
	for(var i=0; i<fileInput.files.length; i++){
		filename = fileInput.files[i].name;
		if(filename.includes("config") || filename.includes("training")){
			uploadfile('myFile1','myProgress_upldtrainingdata1','myBar_upldtrainingdata1','ico_upldtrainingcompleted1','ico_upldtrainingfailed1');
		}
		else{
			alert("Please select correct file");
		}
	}	
	document.getElementById("myFile1").value="";
	document.getElementById("demo1").innerHTML ="";
});

// common function to upload file in server side
function uploadfile(fileinputname,progress,progressbar,completeicon,failureicon){
	var fileInput = document.getElementById(fileinputname); 
	var filename = "";  
	console.log("+++files length++++++++ " + fileInput.files.length);
	let files = new FormData(), // you can consider this as 'data bag'
		url = '/api/fileupload';
	// console.log("===at first files=== " + files.)
	for(var i=0; i<fileInput.files.length; i++){
		// files.append('fileName', $('#myFile')[0].files[i]);
		displayprogressbar(progress,progressbar,10);
		filename = fileInput.files[i].name;
		var filetype="";
		if(filename.includes("intents")){
			filetype="intents";
		}
		else if(filename.includes("config")){
			filetype="config";
		}
		else if(filename.includes("training")){
			filetype="training";
		}
		console.log("+++files++++++++ " + filename)
		console.log("+++files content+++: " + fileInput.files[i])
		// files.append('fileName', fileInput.files[i]);
		headers = {'filename': filename, 'filetype':filetype}
		$.ajax({
			type: 'post',
			url: url,
			processData: false,
			contentType: 'application/json',
			headers: headers,
			data: fileInput.files[i],			
			success: function (response) {
				hideprogressbar(progress);
				console.log(response);
				if(response == "True"){
					document.getElementById(completeicon).hidden=false;
				}else{
					document.getElementById(failureicon).hidden=false;
				}				
			},
			error: function (err) {
				hideprogressbar(progress);
				console.log(err);
				document.getElementById(failureicon).hidden=false;
			}
		});
		
	}	
}

// Populating select client dropbox dynamically
function populateclientdropdown(){
	document.getElementById("ico_completed").hidden=true;
	document.getElementById("ico_failed").hidden=true;
	document.querySelector(('#trainingdiv #runtrainingstatusmsg')).hidden=true;
	document.querySelector(('#trainingdiv #runtrainingstatusmsg')).innerHTML="";
	let dropdown = document.getElementById('client-dropdown');
	// dropdown.length = 0;
	if(dropdown.length>0){

	}
	else{		
		let defaultOption = document.createElement('option');
		defaultOption.text = '- choose -';
		defaultOption.value = 'choose';

		dropdown.add(defaultOption);
		// dropdown.selectedIndex = 0;

		const url = '/api/getclients';

		const request = new XMLHttpRequest();
		request.open('GET', url, true);

		request.onload = function() {
			if (request.status === 200) {
				const data = JSON.parse(request.responseText);
				let option;
				// for (let i = 0; i < data.length; i++) {
				// option = document.createElement('option');
				// option.text = data["client"+i];
				// option.value = data["client"+i];
				// dropdown.add(option);
				// }
				for (x in data){
					option = document.createElement('option');
					option.text = data[x];
					option.value = data[x];
					dropdown.add(option);
				}
				index = dropdown.selectedIndex;
				console.log("index=============" + dropdown.text);
				dropdown.selectedIndex = index;
			} else {
				// Reached the server, but it returned an error
			}   
		}

		request.onerror = function() {
		console.error('An error occurred fetching the JSON from ' + url);
		};

		request.send();
	}
	
}


