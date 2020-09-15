// The ConversationPanel module is designed to handle
// all display and behaviors of the conversation column of the app.
/* eslint no-unused-vars: "off" */
/* global Api: true, Common: true*/
//require("./api");
var conversationId = null;
var counter = 0;
var socket = io();
var event_name = "";

console.log("browser type: " + navigator.vendor);
socket.on("connect", function() {
  console.log("Connected!");
  console.log("Socket ID: " + socket.id);
  event_name = socket.id+"_my_message";
  socket.emit('my_custom_event', {'data': 'I\'m connected!', 'sockid': socket.id});
  console.log("after event emit");

});
socket.on("response", function(json){
  console.log("Inside response!");
  console.log("Response from server after connection event emit: " + JSON.parse(json).msg);

});
socket.on("disconnect", () => {
  console.log("Lost connection to the server.");  
});

function load_welcome(){
	// alert("Image is loaded");
    // console.log("showgreetingmsg=============: " + socket.id);
    // Api.sendRequest("welcome", "");
    // // console.log("showgreetingmsg=============: " + socket.id);
    // console.log("event_name: " + event_name);
    // socket.on(event_name, function(logMessage){ 
    // console.log("Socket ID: " + socket.id);       
    // console.log("*********** showgreetingmsg from socket server *******"+JSON.stringify(logMessage));		  
    // var newPayLoad = null;
    // newPayLoad = {"output" : {"text" :logMessage}};
    // ConversationPanel.displayMessage(newPayLoad, 'watson');	
    // document.getElementById("textInput").disabled = false;
    // document.getElementById("textInput").focus();	  
    // });	
  }


var ConversationPanel = (function() {
	
  var settings = {
    selectors: {
      chatBox: '#scrollingChat',
      fromUser: '.from-user',
      fromWatson: '.from-watson',
      latest: '.latest'
    },
    authorTypes: {
      user: 'user',
      watson: 'watson'
    }
  };

  // Publicly accessible methods defined
  return {
    init: init,
    inputKeyDown: inputKeyDown,
	  instantiateEventHanders: instantiateEventHanders,
    displayMessage: displayMessage
    // showgreetingmsg: showgreetingmsg
  };

  // Initialize the module
  function init() {
	  console.log("inside init.....");
    chatUpdateSetup();
    // var context = {};
	  // context["user_name"] = context.conversation_id;	 
	  // Api.sendRequest( '', context );
    setupInputBox();
  }
  // Set up callbacks on payload setters in Api module
  // This causes the displayMessage function to be called when messages are sent / received
  function chatUpdateSetup() {
    var currentRequestPayloadSetter = Api.setRequestPayload;
    Api.setRequestPayload = function(newPayloadStr) {
      currentRequestPayloadSetter.call(Api, newPayloadStr);
      displayMessage(JSON.parse(newPayloadStr), settings.authorTypes.user);
    };

    var currentResponsePayloadSetter = Api.setResponsePayload;
    Api.setResponsePayload = function(newPayloadStr) {
      currentResponsePayloadSetter.call(Api, newPayloadStr);
      displayMessage(JSON.parse(newPayloadStr), settings.authorTypes.watson);
    };
  }

// Set up the input box to underline text as it is typed
  // This is done by creating a hidden dummy version of the input box that
  // is used to determine what the width of the input text should be.
  // This value is then used to set the new width of the visible input box.
  function setupInputBox() {
    var input = document.getElementById('textInput');
    var dummy = document.getElementById('textInputDummy');
    var minFontSize = 14;
    var maxFontSize = 16;
    var minPadding = 4;
    var maxPadding = 6;

    // If no dummy input box exists, create one
    if (dummy === null) {
      var dummyJson = {
        'tagName': 'div',
        'attributes': [{
          'name': 'id',
          'value': 'textInputDummy'
        }]
      };

      dummy = Common.buildDomElement(dummyJson);
      document.body.appendChild(dummy);
    }

    function adjustInput() {
      if (input.value === '') {
        // If the input box is empty, remove the underline
        input.classList.remove('underline');
        input.setAttribute('style', 'width:' + '100%');
        input.style.width = '100%';
      } else {
        // otherwise, adjust the dummy text to match, and then set the width of
        // the visible input box to match it (thus extending the underline)
        input.classList.add('underline');
        var txtNode = document.createTextNode(input.value);
        ['font-size', 'font-style', 'font-weight', 'font-family', 'line-height',
          'text-transform', 'letter-spacing'].forEach(function(index) {
            dummy.style[index] = window.getComputedStyle(input, null).getPropertyValue(index);
          });
        dummy.textContent = txtNode.textContent;

        var padding = 0;
        var htmlElem = document.getElementsByTagName('html')[0];
        var currentFontSize = parseInt(window.getComputedStyle(htmlElem, null).getPropertyValue('font-size'), 10);
        if (currentFontSize) {
          padding = Math.floor((currentFontSize - minFontSize) / (maxFontSize - minFontSize)
            * (maxPadding - minPadding) + minPadding);
        } else {
          padding = maxPadding;
        }

        var widthValue = ( dummy.offsetWidth + padding) + 'px';
        input.setAttribute('style', 'width:' + widthValue);
        input.style.width = widthValue;
      }
    }

    // Any time the input changes, or the window resizes, adjust the size of the input box
    input.addEventListener('input', adjustInput);
    window.addEventListener('resize', adjustInput);

    // Trigger the input event once to set up the input box and dummy element
    Common.fireEvent(input, 'input');
  }

  // Display a user or Watson message that has just been sent/received
  function displayMessage(newPayload, typeValue) {
  console.log("*******inside displayMessage ");	
  console.log("*******inside displayMessage typeValue : " + typeValue);
  // console.log("*******inside displayMessage newPayload : " + JSON.stringify(newPayload));
  console.log("*******inside displayMessage newPayload.output : " + typeof newPayload);
  // newPayload = JSON.parse(newPayload);
  // console.log("*******inside displayMessage newPayload.output : " + typeof newPayload);
    var isUser = isUserMessage(typeValue);
    if (newPayload.input)
    	console.log("=====newPayload.input==== "+newPayload.input.text);
    if (newPayload.output)
    	console.log("=====newPayload.output==== "+newPayload.output.text);
    var textExists = (newPayload.input && newPayload.input.text && (newPayload.input.text != "context_setter_message")&& (newPayload.input.text != "context_setter_error_message")&& (newPayload.input.text != "context_setter_wait_message"))
      || (newPayload.output && newPayload.output.text);
    console.log("*******inside displayMessage textExists: "+textExists);
    
    if (isUser !== null && textExists) {
      // Create new message DOM element
      var messageDivs = buildMessageDomElements(newPayload, isUser);
      var chatBoxElement = document.querySelector(settings.selectors.chatBox);
      var previousLatest = chatBoxElement.querySelectorAll((isUser
              ? settings.selectors.fromUser : settings.selectors.fromWatson)
              + settings.selectors.latest);
      // Previous "latest" message is no longer the most recent
      if (previousLatest) {
        Common.listForEach(previousLatest, function(element) {
          element.classList.remove('latest');
        });
      }

      messageDivs.forEach(function(currentDiv) {
        chatBoxElement.appendChild(currentDiv);
        // Class to start fade in animation
        currentDiv.classList.add('load');
      });
      // Move chat to the most recent messages when new messages are added
      scrollToChatBottom();    
      if(!isUser){
        Voice.synthVoice(textExists);
        // Voice.startvoice();
      }  
    }
  }

  // Checks if the given typeValue matches with the user "name", the Watson "name", or neither
  // Returns true if user, false if Watson, and null if neither
  // Used to keep track of whether a message was from the user or Watson
  function isUserMessage(typeValue) {
    if (typeValue === settings.authorTypes.user) {
      return true;
    } else if (typeValue === settings.authorTypes.watson) {
      return false;
    }
    return null;
  }

  // Constructs new DOM element from a message payload
  function buildMessageDomElements(newPayload, isUser) {
    //var textArray = isUser ? newPayload.input.text : newPayload.output.text;
	
	var textArray = isUser ? newPayload.input.text+"<I><font size='1.5'>"+displayTime()+"</font></I>" : newPayload.output.text+"<I><font size='1.5'>"+displayTime()+"</font></I>";
    if (Object.prototype.toString.call( textArray ) !== '[object Array]') {
      textArray = [textArray];
    }
    var messageArray = [];

    textArray.forEach(function(currentText) {
      if (currentText) {
        var messageJson = {
          // <div class='segments'>
          'tagName': 'div',
          'classNames': ['segments'],
          'children': [{
            // <div class='from-user/from-watson latest'>
            'tagName': 'div',
            'classNames': [(isUser ? 'from-user' : 'from-watson'), 'latest', ((messageArray.length === 0) ? 'top' : 'sub')],
            'children': [{
              // <div class='message-inner'>
              'tagName': 'div',
              'classNames': ['message-inner'],
              'children': [{
                // <p>{messageText}</p>
                'tagName': 'p',
                'text': currentText
              }]
            }]
          }]
        };
        messageArray.push(Common.buildDomElement(messageJson));
      }
    });

    return messageArray;
  }

  // Scroll to the bottom of the chat window (to the most recent messages)
  // Note: this method will bring the most recent user message into view,
  //   even if the most recent message is from Watson.
  //   This is done so that the "context" of the conversation is maintained in the view,
  //   even if the Watson message is long.
  function scrollToChatBottom() {
    var scrollingChat = document.querySelector('#scrollingChat');

    // Scroll to the latest message sent by the user
    var scrollEl = scrollingChat.querySelector(settings.selectors.fromUser
            + settings.selectors.latest);
    if (scrollEl) {
      scrollingChat.scrollTop = scrollEl.offsetTop;
    }
  }  

  // Handles the submission of input
  function inputKeyDown(event, inputBox) {
    // Submit on enter key, dis-allowing blank messages
    // Voice.startvoice();
    console.log("***inside inputKeyDown");
    console.log("***inside inputBox value : " + inputBox.value);
    if (event.keyCode === 13 && inputBox.value != "") {
      // Retrieve the context from the previous server response
      var context = "";
      // var latestResponse = Api.getResponsePayload();
      // console.log("=======================: " + latestResponse);
    //   if (latestResponse) {
    //     context = latestResponse.context;
		// conversationId = context.conversation_id;
    //   }
	  // console.log("=======in converstaion.js.inputKeyDown before "+context.conversation_id);
      // Send the user message
      Api.sendRequest(inputBox.value, context);
      // console.log("=======in converstaion.js.inputKeyDown after "+context.conversation_id);
      console.log("=======in converstaion.js.inputKeyDown after " + inputBox.value);
      // Clear input box for further messages
      inputBox.value = '';
      inputBox.placeholder = 'Type something';
      Common.fireEvent(inputBox, 'input');
      console.log("++++inputKeyDown========Socket ID: " + socket.id)
      
    }
  }
  
 
  function instantiateEventHanders(event){		  
  // if(event.key=='Enter' && counter==0){
  if((event.key=='Enter'||event.type=='result') && counter==0){
  console.log("***inside instantiateEventHanders");
  // print("***inside instantiateEventHanders")
  // const socket = io('ws://localhost:5000');
  var socket = io();
  counter++;
	var user = conversationId;
  // console.log("HHHHHHHHHHHHHH conversationId    "+user);	
    // Add a connect listener
    // socket.on('connect',function() {
    //   console.log('Client has connected to the server!');
    //   console.log("Socket ID: " + socket.id)
    //   // console.log("Socket ID: " + socket.server.ip)
    // });   
    // socket.send("message","my hello from client send") 
    // socket.emit("message", "my hello from client emit");    
    // var even_name = socket.id+"_my_message"
    console.log("event_name: " + event_name);
		socket.on(event_name, function(logMessage){ 
      console.log("Socket ID: " + socket.id);     
      socket.emit("client_message","my hello from client send")
		  console.log("*********** input_context from socket client *******"+JSON.stringify(logMessage));		  
			  var newPayLoad = null;
				newPayLoad = {"output" : {"text" :logMessage}};
        ConversationPanel.displayMessage(newPayLoad, 'watson');	
        document.getElementById("textInput").disabled = false;
		    document.getElementById("textInput").focus();	  
    });	
    // Add a disconnect listener
    // socket.on('disconnect',function() {
    //   console.log('The client has disconnected!');
    // });
    // Sends a message to the server via sockets
    // function sendMessageToServer() {
    //   socket.send("This is a hi from client");
    // };
	}
 }

  
}());


function displayTime() {
    var str = "";

    var currentTime = new Date()
	var date = currentTime.getDate()
	var month = currentTime.getMonth()+1;
	var year = currentTime.getFullYear();
    var hours = currentTime.getHours()
    var minutes = currentTime.getMinutes()
    var seconds = currentTime.getSeconds()

    if (minutes < 10) {
        minutes = "0" + minutes
    }
    if (seconds < 10) {
        seconds = "0" + seconds
    }
    str += "<br>"+month+"/"+date+"/"+year+",  "+hours + ":" + minutes + ":" + seconds + " ";
    if(hours > 11){
        str += "PM"
    } else {
        str += "AM"
    }
    return str;
}

function clertext(){
  document.getElementById("textInput").value = ""
}