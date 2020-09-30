var websocket;
var websocket_url = "wss://35.222.34.232:6789/";
var current_connection_id = 0;

var mediaRecorder = 0;
var audioPlayer = 0;
var audioChunks = [];
var audioArray;
var arrayBuffer;
var recording = 0;
var soundOn = 1;


function verifyConnection() {
  if (websocket.readyState == 1) {
    $('.connection_message').remove();
  } else {
    if ($('.connection_message').length == 0)
      $('.chatbot_client_container').append('<div class="connection_message">Waiting for connection...</div>');
    if (websocket.readyState == 3)
      initWebSocket();
  }
}

function initWebSocket() {
   websocket = new WebSocket(websocket_url);
   websocket.onmessage = function (event) {
       data = JSON.parse(event.data);
       $('#bot_waiting').remove();
       if (data.type == "connection_id") {
         if (current_connection_id == 0) {
           current_connection_id = data.connection_id;
           websocket.send(JSON.stringify({
             type: 'connection_id',
             connection_id: current_connection_id
           }));
         } else {
           websocket.send(JSON.stringify({
             type: 'connection_id',
             connection_id: current_connection_id
           }));
           current_connection_id = data.connection_id;
         }
       }
       else if (data.type == "first_message") {
         $('.bot_message').remove();
         $('.user_message').remove();
         $('.chatbot_client_container').append('<div class="bot_message"><div>'+data.message+'</div></div>');
         if (data.audio) {
           playAudio(data.audio);
         }
       }
       else if (data.type == "list_options") {
         $('.chatbot_client_container').append('<div class="bot_message"><div>'+data.message+'</div></div>');
         options_html = "";
         for (var i=0; i<data.options.length; i++) {
           options_html += '<div class="food_option">'
            +'<h2>'+data.options[i]['name']+' <span>'+data.options[i]['price']+'$</span></h2>'
            +'<img src="assets/images/food_images/'+data.options[i]['id']+'.jpg" />'
            +'</div>';
         }
         $('.chatbot_client_container').append('<div class="bot_message"><div>'+options_html+'</div></div>');
         if (data.audio) {
           playAudio(data.audio);
         }
         scrollContainer();
       } else if (data.type == "audio_response") {
         if (data.message) {
            $('#chatbot_client_input_text').val(data.message);
            if (data.audio) {
              playAudio(data.audio);
            }
         }
       } else {
         $('.chatbot_client_container').append('<div class="bot_message"><div>'+data.message+'</div></div>');
         if (data.audio) {
           playAudio(data.audio);
         }
         scrollContainer();
       }

   };
}

function scrollContainer() {
  var s = $('.chatbot_client_container')[0].scrollHeight;
  $('.chatbot_client_container').animate({scrollTop:s}, '1000');
}

function constructLanguageButton() {
  var languages=[{name:"Afrikaans",code:"af"},{name:"Albanian",code:"sq"},{name:"Amharic",code:"am"},{name:"Arabic",code:"ar"},{name:"Armenian",code:"hy"},{name:"Azerbaijani",code:"az"},{name:"Basque",code:"eu"},{name:"Belarusian",code:"be"},{name:"Bengali",code:"bn"},{name:"Bosnian",code:"bs"},{name:"Bulgarian",code:"bg"},{name:"Catalan",code:"ca"},{name:"Cebuano",code:"ceb"},{name:"Chinese (Simplified)",code:"zh-CN"},{name:"Chinese (Traditional)",code:"zh-TW"},{name:"Corsican",code:"co"},{name:"Croatian",code:"hr"},{name:"Czech",code:"cs"},{name:"Danish",code:"da"},{name:"Dutch",code:"nl"},{name:"English",code:"en"},{name:"Esperanto",code:"eo"},{name:"Estonian",code:"et"},{name:"Finnish",code:"fi"},{name:"French",code:"fr"},{name:"Frisian",code:"fy"},{name:"Galician",code:"gl"},{name:"Georgian",code:"ka"},{name:"German",code:"de"},{name:"Greek",code:"el"},{name:"Gujarati",code:"gu"},{name:"Haitian Creole",code:"ht"},{name:"Hausa",code:"ha"},{name:"Hawaiian",code:"haw"},{name:"Hebrew",code:"he"},{name:"Hindi",code:"hi"},{name:"Hmong",code:"hmn"},{name:"Hungarian",code:"hu"},{name:"Icelandic",code:"is"},{name:"Igbo",code:"ig"},{name:"Indonesian",code:"id"},{name:"Irish",code:"ga"},{name:"Italian",code:"it"},{name:"Japanese",code:"ja"},{name:"Javanese",code:"jv"},{name:"Kannada",code:"kn"},{name:"Kazakh",code:"kk"},{name:"Khmer",code:"km"},{name:"Kinyarwanda",code:"rw"},{name:"Korean",code:"ko"},{name:"Kurdish",code:"ku"},{name:"Kyrgyz",code:"ky"},{name:"Lao",code:"lo"},{name:"Latin",code:"la"},{name:"Latvian",code:"lv"},{name:"Lithuanian",code:"lt"},{name:"Luxembourgish",code:"lb"},{name:"Macedonian",code:"mk"},{name:"Malagasy",code:"mg"},{name:"Malay",code:"ms"},{name:"Malayalam",code:"ml"},{name:"Maltese",code:"mt"},{name:"Maori",code:"mi"},{name:"Marathi",code:"mr"},{name:"Mongolian",code:"mn"},{name:"Myanmar (Burmese)",code:"my"},{name:"Nepali",code:"ne"},{name:"Norwegian",code:"no"},{name:"Nyanja (Chichewa)",code:"ny"},{name:"Odia (Oriya)",code:"or"},{name:"Pashto",code:"ps"},{name:"Persian",code:"fa"},{name:"Polish",code:"pl"},{name:"Portuguese (Portugal, Brazil)",code:"pt"},{name:"Punjabi",code:"pa"},{name:"Romanian",code:"ro"},{name:"Russian",code:"ru"},{name:"Samoan",code:"sm"},{name:"Scots Gaelic",code:"gd"},{name:"Serbian",code:"sr"},{name:"Sesotho",code:"st"},{name:"Shona",code:"sn"},{name:"Sindhi",code:"sd"},{name:"Sinhala (Sinhalese)",code:"si"},{name:"Slovak",code:"sk"},{name:"Slovenian",code:"sl"},{name:"Somali",code:"so"},{name:"Spanish",code:"es"},{name:"Sundanese",code:"su"},{name:"Swahili",code:"sw"},{name:"Swedish",code:"sv"},{name:"Tagalog (Filipino)",code:"tl"},{name:"Tajik",code:"tg"},{name:"Tamil",code:"ta"},{name:"Tatar",code:"tt"},{name:"Telugu",code:"te"},{name:"Thai",code:"th"},{name:"Turkish",code:"tr"},{name:"Turkmen",code:"tk"},{name:"Ukrainian",code:"uk"},{name:"Urdu",code:"ur"},{name:"Uyghur",code:"ug"},{name:"Uzbek",code:"uz"},{name:"Vietnamese",code:"vi"},{name:"Welsh",code:"cy"},{name:"Xhosa",code:"xh"},{name:"Yiddish",code:"yi"},{name:"Yoruba",code:"yo"},{name:"Zulu",code:"zu"}];
  var button = '<select id="chatbot_client_language_select">';
  for (var i=0; i<languages.length; i++) {
    button += '<option value="'+languages[i]['code']+'">'+languages[i]['name']+'</option>';
  }
  button += '</select>';
  return button;
}

function initChat() {
  $('#chatbot_client').html(
    '<div class="chatbot_client_header">Food Order Bot'+constructLanguageButton()
    +'<button id="chatbot_client_audio_button"></button>'
    +'</div>'
    +'<div class="chatbot_client_container">'
    +'</div>'
    +'<div class="chatbot_client_input">'
    +  '<input type="text" name="chatbot_client_input" placeholder="Type a message..." id="chatbot_client_input_text" />'
    +  '<button id="chatbot_client_input_button"></button>'
    +  '<button id="chatbot_client_mic_button"></button>'
    +'</div>'
  );
  $('#chatbot_client_language_select').val('en');
  $('#chatbot_client_input_button').click(onSendMessage);
  $('#chatbot_client_language_select').change(onLanguageChange);
  $('#chatbot_client_mic_button').click(onMicClick);
  $('#chatbot_client_audio_button').click(onAudioClick);
  $('#chatbot_client_input_text').keyup(onInputKeyUp);
}

function onLanguageChange() {
  var language_code = $('#chatbot_client_language_select').val();
  current_language_code = language_code;
  websocket.send(JSON.stringify({
    type: 'language_code',
    language_code: language_code
  }));
}

function onInputKeyUp(e) {
  if (e.keyCode == 13) {
    onSendMessage();
  }
}

function onSendMessage() {
  var text = $('#chatbot_client_input_text').val();
  $('#chatbot_client_input_text').val('');
  if (websocket.readyState == 1) {
    websocket.send(JSON.stringify({
      type: 'text',
      message: text
    }));
    $('.chatbot_client_container').append('<div class="user_message"><div>'+text+'</div></div>');
    $('.chatbot_client_container').append('<div class="bot_message" id="bot_waiting"><div>...</div></div>');
    scrollContainer();
  }
}


function onAudioClick() {
  if (soundOn) {
    $('#chatbot_client_audio_button').addClass("off");
    soundOn = 0;
    if (audioPlayer) {
      audioPlayer.pause();
    }
  } else {
    $('#chatbot_client_audio_button').removeClass("off");
    soundOn = 1;

  }
}

function onMicClick() {
  if (recording == 0)
    recordStart();
  else
    recordStop();
}

function recordStart() {
  $('#chatbot_client_mic_button').addClass("recording");
  recording = 1;
  if (audioPlayer) {
    audioPlayer.pause();
  }
  mediaRecorder.start();
  window.setTimeout(recordAutoStop, 10000);
}

function recordStop() {
  $('#chatbot_client_mic_button').removeClass("recording");
  recording = 0;
  mediaRecorder.stop();
  //audioBlob = new Blob(audioChunks, { 'type' : 'audio/webm; codecs=opus' });
}

function recordAutoStop() {
  if (recording) {
    recordStop();
  }
}


function getAudioMediaStream() {
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
   console.log('getUserMedia supported.');
   navigator.mediaDevices.getUserMedia (
      // constraints - only audio needed for this app
      {
         audio: true
      })

      // Success callback
      .then(function(stream) {
        var options = {
          audioBitsPerSecond: 44100,
        }
          mediaRecorder = new MediaRecorder(stream, options);
          mediaRecorder.ondataavailable = function(e) {
            audioChunks.push(e.data);
          }
          mediaRecorder.onstop = function(e) {
            sendBlob();
            audioChunks = [];
          }
      })

      // Error callback
      .catch(function(err) {
         console.log('The following getUserMedia error occured: ' + err);
      }
   );
} else {
  $('#chatbot_client_input_button').hide();
   console.log('getUserMedia not supported on your browser!');
}
}

function sendBlob() {
  var audioBlob = new Blob(audioChunks, { 'type' : 'audio/webm; codecs=opus' });
  var xhr = new XMLHttpRequest();
  xhr.onload = function(e) {
      if (this.readyState === 4) {
          console.log("Server returned: ", e.target.responseText);
          var res = JSON.parse(e.target.responseText);
          if (res.response) {
            $('#chatbot_client_input_text').val(res.response);
            onSendMessage();
          }
      }
  };
  var fd = new FormData();
  fd.append("audio_data", audioBlob, new Date().getTime()+".weba");
  //xhr.addEventListener("load", reqListener);
  xhr.open("POST", "https://35.222.34.232:5001/audio_process", true);
  xhr.send(fd);

}

async function playAudio(uid) {
  audioPlayer = new Audio('assets/audios/'+uid+'.mp3');
  audioPlayer.type = 'audio/mp3';
  if (soundOn) {
    try {
      await audioPlayer.play();
      console.log('Playing...');
    } catch (err) {
      console.log('Failed to play...' + err);
    }
  }
}




window.onload = function() {
  initChat();
  getAudioMediaStream();
  initWebSocket();
  window.setInterval(verifyConnection, 1000);
}
