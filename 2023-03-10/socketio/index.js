const express = require("express");
const app = require('express')();
const http = require('http').Server(app);
const io = require('socket.io')(http);
const port = process.env.PORT || 3000;
const net = require('node:net');
const path = require("path");
const timestamp = require("time-stamp");

const LOG_SRC = {"DATA_BRIDGE":"DATA_BRIDGE",
                 "HTTP":"HTTP",
                 "BUTTON":"BUTTON"};

const LOG_TYPE = {"RECV":"RECV",
                  "SEND":"SEND",
                  "INIT":"INIT",
                  "CONN":"CONN",
                  "DCON":"DCON"};

const log = (source, type, msg) => {
  console.log(`[${timestamp("YYYY:MM:DD:HH:mm:ss")}] [${source}] [${type}] - ${msg.toString()}`);
}

app.use("/assets", express.static(path.join(__dirname, "assets")));

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/index.html');
});
app.get('/buttons', (req, res) => {
  res.sendFile(__dirname + '/buttons.html');
});


io.on('connection', (socket) => {
  /*
  socket.on('chat message', msg => {
    http_io.emit('chat message', msg);
  });
  */
  socket.on("info_request", msg => {
    log(LOG_SRC.HTTP, LOG_TYPE.RECV, msg.toString());
    log(LOG_SRC.DATA_BRIDGE, LOG_TYPE.SEND, msg.toString());

    client.write("info_request");
  });
});

http.listen(port, () => {
  log(LOG_SRC.HTTP, LOG_TYPE.INIT, `http://192.168.0.6:${port}`);
});

const client = net.createConnection({ host:"192.168.0.6", port:12889 }, () => {
});

client.on("connect", () => {
  log(LOG_SRC.DATA_BRIDGE, LOG_TYPE.CONN, "192.168.0.6:12889");
});

client.on("data", (data) => {
  let data_string = data.toString();
  log(LOG_SRC.DATA_BRIDGE, LOG_TYPE.RECV, data.toString())
  if (data_string == "b'Fart'") {
    io.emit("fart", data_string);
  } else if (data_string == "b'mario_oof'") {
    io.emit("mario_oof", data_string);
  } else if (data_string == "b'laugh_track'") {
    io.emit("laugh_track", data_string);
  } else if (data_string == "b'clapping'") {
    io.emit("clapping", data_string);
  } else {
    io.emit("job_applications", data_string);
  }
});

client.on("end", () => {
  log(LOG_SRC.DATA_BRIDGE, LOG_TYPE.DCON, "Disconnected");
});

client.on("error", (err) => {
  if (err.message.indexOf("read ECONNRESET") != -1) {
    log(LOG_SRC.DATA_BRIDGE, LOG_TYPE.DCON, "Connection reset.");
    setTimeout(()=>{
      log(LOG_SRC.DATA_BRIDGE, LOG_TYPE.DCON, "Reconnecting...");
      client.connect(12889, "192.168.0.6");
    },5000);
  } else if (err.message.indexOf("connect ECONNREFUSED") != -1) {
    log(LOG_SRC.DATA_BRIDGE, LOG_TYPE.DCON, "Connection refused.");
    setTimeout(()=>{
      log(LOG_SRC.DATA_BRIDGE, LOG_TYPE.DCON, "Retrying...");
      client.connect(12889, "192.168.0.6");
    },5000);
  } else {
    throw err;
  }
});
