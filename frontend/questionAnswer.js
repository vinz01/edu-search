'use strict';
var id;
var url;
var count_row = 0;
chrome.tabs.query({'active': true, 'currentWindow': true}, function (tabs) {
  url = tabs[0].url;
  id = url.split('v=')[1]
});

function runCommand(st) {
    // document.write(st)
    chrome.tabs.query({active: true, lastFocusedWindow: true}, function(tabs) {
      var url = tabs[0].url
      var index = url.lastIndexOf("#t")
      if(index>0)
        chrome.tabs.update(tabs[0].id, {url: url.substring(0,index) + "#t="+st});
      else
      chrome.tabs.update(tabs[0].id, {url: url + "#t="+st});


    });

  }

  function fetchya(word,id){
   
    // document.write(word+id)
    fetch('http://127.0.0.1:5003/'+ word +'/' + id).then(r => r.text()).then(result => {

      
      var mydata = JSON.parse(result);
      // document.write(mydata.length)
      var i;
      var x = [];

      if (mydata.length == 0) {
        var temp = document.getElementById('answer')
        temp.innerHTML = "Word not found in Video, or very trivial. Please try another keyword!"
      }else{
        var span_notFound = document.getElementById('answer');
      span_notFound.innerHTML = mydata[0].answer;
      }
      for (var i = 1; i < mydata.length; i++) {     
            var row = table.insertRow(-1);
            var cell2 = row.insertCell(-1);
            var index = mydata[i].phrase.indexOf(word);
            if (index >= 0) { 
              mydata[i].phrase = mydata[i].phrase.substring(0,index) +  "<mark>" + mydata[i].phrase.substring(index,index+word.length) + "</mark>" + mydata[i].phrase.substring(index + word.length);
            }
            cell2.innerHTML = ". . . " + mydata[i].phrase + " . . .";
            var cell = row.insertCell(-1);
            // var l = document.createElement("BUTTON");
            // l.setAttribute("id", mydata[i].timestamp)
            cell.innerHTML = "<input type = \"button\"  class = \"btn btn-info\" style = \"width: 100%;'font-family: \"Source Sans Pro\"; color: \"#ffffff\";\" id = \"" +  mydata[i].timestamp + "\" value = \"" + mydata[i].timestamp +"\" onclick = runCommand("+mydata[i].timestamp+"\">"
            document.getElementById(mydata[i].timestamp).addEventListener("click", function(e) {
              // alert(this.id)
              runCommand(this.id)
            });
            count_row++;
            
    }
    

  });
  

  }

var word;

  window.addEventListener('load', () => {
    document.getElementById('form').addEventListener('submit', function(evt) {
      evt.preventDefault();
      word = document.getElementById('question').value;
      var span_notFound = document.getElementById('answer');
        span_notFound.innerHTML = "Loading Results...";
      setTimeout(() => {
           fetchya(word,id)
      }, 1000)
    })
  })