// Copyright 2018 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

'use strict';

// var span_notFound = document.getElementById('not-found');
// span_notFound.innerHTML = "";

var count_row=0;
var id;
var url;
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
    fetch('http://127.0.0.1:5004/'+ word +'/' + id).then(r => r.text()).then(result => {

      
      var mydata = JSON.parse(result);
      // document.write(mydata.length)
      var i;
      var x = [];

      var table = document.getElementById("tbody");


      if (mydata.length == 0) {
        var temp = document.getElementById('not-found')
        temp.innerHTML = "Word not found in Video, or very trivial. Please try another keyword!"
      }else{
        var span_notFound = document.getElementById('not-found');
      span_notFound.innerHTML = "";
      var summary1 = document.getElementById('summaryText_1');
      var summary2 = document.getElementById('summaryText_2');
      var summary3 = document.getElementById('summaryText_3');  
      summary1.innerHTML = mydata.p_summary;
      summary2.innerHTML = mydata.n_summary;
      summary3.innerHTML = mydata.nu_summary;
      }
      
      

  });
  

  }

var word;
window.addEventListener('load', () => {
  document.getElementById('form').addEventListener('submit', function(evt) {
    evt.preventDefault();
    word=document.getElementById('word').value;
    var span_notFound = document.getElementById('not-found');
    span_notFound.innerHTML = "Loading Results...";
    setTimeout(() => {
        fetchya(word,id)
    }, 1000)
  })
})
