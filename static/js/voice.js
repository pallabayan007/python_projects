'use strict';
// The voice module is designed to handle all voice related interactions with the server

const SpeechRecognition = window.SpeechRecognition|| window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
// const recognition =

recognition.lang = 'en-US';
recognition.interimResults = false;
recognition.maxAlternatives = 1;

// document.querySelector('speech_button').click
// document.querySelector('speech_button').click('click', () => {
//   recognition.start();
//   console.log("started voice logging");
// });

recognition.addEventListener('speechstart', () => {
  console.log('Speech has been detected.');
});

recognition.addEventListener('result', (e) => {
  console.log('Result has been detected.');

  let last = e.results.length - 1;
  let text = e.results[last][0].transcript;

  // outputYou.textContent = text;
  console.log('Confidence: ' + e.results[0][0].confidence);
  console.log('text transcript: ' + e.results[last][0].transcript);
  console.log('text: ' + text);
  // socket.emit('chat message', text);
});

recognition.addEventListener('speechend', () => {
  recognition.stop();
});

recognition.addEventListener('error', (e) => {
  // outputBot.textContent = 'Error: ' + e.error;
  console.log('Error: ' + e.error);
});


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
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance();
    utterance.text = text;
    synth.speak(utterance);
  }

}());
