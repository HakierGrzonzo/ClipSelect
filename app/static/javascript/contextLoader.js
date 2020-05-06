usedIDs = [];

function loadContext(id) {
  var div = $("#"+id).get(0);
  if (usedIDs.includes(id)) {

  } else {
    usedIDs.push(id);
    getJSON('/quoteCard/'+id, function(err, data) {
      if (err !== null) {
        console.warn('error in loadContext');
        console.warn(err);
      } else {
        var dom = div.getElementsByClassName('postQuote')[0];
        console.log(data.content);
        dom.getElementsByTagName('span')[0].innerHTML = data[1].content;
        anime({
          targets: dom,
          scale: .8,
          easing: 'easeInOutQuad'
        });
        var dom = div.getElementsByClassName('preQuote')[0];
        console.log(data.content);
        dom.getElementsByTagName('span')[0].innerHTML = data[0].content;
        anime({
          targets: dom,
          scale: .8,
          easing: 'easeInOutQuad'
      });
    }});
  }
}
var getJSON = function(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.responseType = 'json';
    xhr.onload = function() {
      var status = xhr.status;
      if (status === 200) {
        callback(null, xhr.response);
      } else {
        callback(status, xhr.response);
      }
    };
    xhr.send();
};
