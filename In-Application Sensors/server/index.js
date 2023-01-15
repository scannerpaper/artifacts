const express = require('express')
const bodyParser = require("body-parser");
const cors = require('cors');
const uuid = require('uuid');
const app = require('express')();

function saveInDB() {}

const server = require('http').Server(app);
const io = require('socket.io')(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST", "PUT"],
    allowedHeaders: ["custom-header"],
    credentials: true
  }
});

async function main() {
  io.on('connection', socket => {
    const cookie = {
      id: uuid.v4(),
    };
    socket.emit('auth', cookie);
    socket.on('data', data => {
      if (data.data){
        data = data.data
      }
      // ============= Process the events in any way ===================
      // ============= for example just save in a database =============
      // saveInDB(socket.handshake.headers, data);

    });
    
  });

  app.use(bodyParser.urlencoded({ extended: false }));
  app.use(bodyParser.json());
  app.use(cors({
    origin: '*',
  }));

  app.use(express.static('public'));
  server.listen(8080, () => {
    console.log('App listening at http://localhost:8080');
  });
}

main().catch(err => {
  console.log(err);
})
