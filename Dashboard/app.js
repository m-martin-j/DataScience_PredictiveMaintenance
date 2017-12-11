var express = require('express');
var bodyParser = require('body-parser');
var config = require('./config');
var path = require('path');

global.appRoot = path.resolve(__dirname);

var app = express();

app.engine('html', require('ejs').renderFile);
app.set('view engine', 'ejs');

app.use(bodyParser.json());
app.use('/', express.static(__dirname + '/views/static'));
app.use('/', express.static(__dirname + '/node_modules'));

app.use(require('./controllers'));

app.listen(config.web.port, function () {
  console.log('Dashboard started');
});
