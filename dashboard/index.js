var express = require('express');
var app = require('express')();
var http = require('http').Server(app);
var r = require('rethinkdb');
var io = require('socket.io')(http);

var config = require(__dirname+"/config.js")

var connection = null;

io.on('connection', function(socket){
  console.log('a user connected');
});

app.get('/', function(req, res){
  res.sendfile('index.html');
});

r.connect( {host: 'localhost', port: 28015}, function(err, conn) {

    if (err) throw err;
    connection = conn;

  r.db('sentiment').table('messages').changes().run(connection, function(err, cursor) {
    if (err) throw err;
    cursor.each(function(err, row) {
      if (err) throw err;
      //console.log(JSON.stringify(row, null, 2));
      io.emit('feed', JSON.stringify(row, null, 2));
    });
  });

  r.db('sentiment').table('classified_messages').changes().run(connection, function(err, cursor) {
    if (err) throw err;
    cursor.each(function(err, row) {
      if (err) throw err;
      console.log(JSON.stringify(row, null, 2));
      io.emit('classified', JSON.stringify(row, null, 2));
    });
  });

})

app.use(express.static(__dirname));

http.listen(3000, function(){
  console.log('listening on *:3000');
});
