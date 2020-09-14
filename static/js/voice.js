'use strict';
// The voice module is designed to handle all voice related interactions with the server
var voiceRequired = false;
const SpeechRecognition = window.SpeechRecognition|| window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
// const recognition =

recognition.lang = 'en-IN';
recognition.interimResults = false;
recognition.maxAlternatives = 1;
// document.querySelector('speech_button').click
// document.querySelector('speech_button').click('click', () => {
//   recognition.start();
//   console.log("started voice logging");
// });

console.log("browser type: " + navigator.vendor);

if(navigator.vendor.includes("Google")){   
  $("#textInput").click(function(){
    console.log("=====Inside text input click======");
    Voice.startvoice();
    voiceRequired = true;

  });
}

recognition.addEventListener('speechstart', () => {
  console.log('Speech has been detected.');
});

recognition.addEventListener('result', (e) => {  
  console.log('Result has been detected.');

  let last = e.results.length - 1;
  let text = e.results[last][0].transcript;
  let inputbox = document.getElementById("textInput");

  // outputYou.textContent = text;
  console.log('Inside Voice sendapireq=======');
  console.log('Confidence: ' + e.results[0][0].confidence);
  console.log('text transcript: ' + e.results[last][0].transcript);
  console.log('text: ' + text); 
  inputbox.placeholder = text; 
  inputbox.value = text;
  inputbox.focus();
  // $("#textInput").keydown();
  
  // var ev = $.Event("keydown");
  // ev.which = 13;
  // ev.keyCode = 13;
  // $("#textInput").trigger(ev);
  // console.log('after enter========='); 
  // Common.fireEvent(inputbox, 'ENTER');

  clickevent("#textInput");
  // callKeypressEnter(document.getElementById("textInput"));
  // ConversationPanel.inputKeyDown(callKeypressEnter(document.getElementById("textInput")), document.getElementById("textInput"))
  // sendapireq(text);
});

recognition.addEventListener('speechend', () => {
  recognition.stop();
  // voiceRequired = false;
});

recognition.addEventListener('error', (e) => {
  // outputBot.textContent = 'Error: ' + e.error;
  console.log('Error: ' + e.error);
  voiceRequired = false;  
});

function callKeypressEnter(obj){
  // focus on the input element
  console.log("==Inside the keypress event==");
  obj.focus();
  // dispatch keyboard events
  obj.dispatchEvent(new KeyboardEvent('keydown',  {'key':'Enter'}));
      
  // add event listeners to the input element
  obj.addEventListener('keypress', (event) => {
        console.log("You have pressed key: ", event.key);	
  });
}

function clickevent(objselector)
{                
     console.log("==Inside the keypress event==");
     var e = $.Event("keydown");
     e.which = 13;
     e.keyCode = 13;
     $(objselector).trigger(e);     
}

var Voice = (function() {

  // Publicly accessible methods defined
  return {
    synthVoice:synthVoice,
    startvoice:startvoice,   
  };


  function startvoice(){
    recognition.start();
    console.log("started voice logging");
  }

  function synthVoice(text) {
    console.log("===== Inside synthVoice=======");
    console.log("===== Inside synthVoice text=======" + text);
    console.log("===== Inside synthVoice text type=======" + typeof text);
    const synth = window.speechSynthesis;
    console.log("voiceRequired");
    console.log(voiceRequired);
    if(voiceRequired){
      const utterance = new SpeechSynthesisUtterance();
      utterance.text = text;
      synth.speak(utterance);
      utterance.onend = function(e) {
        console.log('Finished in ' + e.elapsedTime + ' seconds.');
        $("#textInput").click();
      };  

    }
      
    // var msg = new SpeechSynthesisUtterance(text);
    // window.speechSynthesis.speak(msg);
    console.log("===== EndOf synthVoice=======");
  }

}());
