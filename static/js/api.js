// The Api module is designed to handle all interactions with the server

var Api = (function() {
  var requestPayload;
  var responsePayload;
  var messageEndpoint = '/api/message';

  // Publicly accessible methods defined
  return {
    sendRequest: sendRequest,

    // The request/response getters/setters are defined here to prevent internal methods
    // from calling the methods without any of the callbacks that are added elsewhere.
    getRequestPayload: function() {
      return requestPayload;
    },
    setRequestPayload: function(newPayloadStr) {
      requestPayload = JSON.parse(newPayloadStr);
    },
    getResponsePayload: function() {
      return responsePayload;
    },
    setResponsePayload: function(newPayloadStr) {
      responsePayload = JSON.parse(newPayloadStr);
    }
  };

  // Send a message request to the server
  function sendRequest(text, context) {
    // Build request payload
    console.log("++++++ inside sendRequest()");
    console.log("++++++ inside sendRequest() & current url: " + window.location.href);
    var url = window.location.href
    var client = url.substr((url.lastIndexOf('/')+1),url.length)
    console.log("++++++ inside sendRequest() & client name: " + client);
    var payloadToWatson = {};
    if (text) {
      console.log('Inside payload text: ' + text)
      console.log('Inside payload text socket id : ' + socket.id)
      payloadToWatson.input = {
        text: text,
        client: client,
        socket_id: socket.id
      };
      console.log('Inside payloadToWatson text: ' + payloadToWatson.input)
    }
    if (context) {
      payloadToWatson.context = context;
    }
//console.log("((((((((text))))))))"+text);
//console.log("TTTTTTTTTTTTTTT  "+context);
    // Built http request
    var http = new XMLHttpRequest();
    //console.log("++++++ http "+http);
    http.open('POST', messageEndpoint, true);
    http.setRequestHeader('Content-type', 'application/json');
    http.onreadystatechange = function() {
      if (http.readyState === 4 && http.status === 200 && http.responseText) {
        console.log("http.responseText: " + http.responseText);
        Api.setResponsePayload(http.responseText);
      }
    };
    //console.log("++++++ http 2"+http.responseText);
    var params = JSON.stringify(payloadToWatson);
    console.log('Inside params text: ' + params)
    // Stored in variable (publicly visible through Api.getRequestPayload)
    // to be used throughout the application
    if (Object.getOwnPropertyNames(payloadToWatson).length !== 0) {
      Api.setRequestPayload(params);
    }
    console.log("++++++ params"+params);
    // Send request
    http.send(params);
  }
}());
//var http = require('http');
/*module.exports = {
callApi: function (txt) {
  console.log("2222 +++++++ callApi +++++");
  var context;
  //var latestResponse = Api.getResponsePayload();
  //if (latestResponse) {
    context = txt;
  //}
  console.log("+++++Context++++++++ "+txt);
    Api.sendRequest('Hello World..',context);
}
};*/
