/* eslint spaced-comment: ["error", "always", { "exceptions": ["="] }] */
var express = require('express');
var app = express();
var routes = require('./server/routes/index');
var bodyParser = require('body-parser');

global.__base = __dirname + '/';

//===============================
// MEI Middleware
//===============================
var handleMEI = function (req, res, next) {
  if (req.is('application/xml') || req.is('application/mei+xml')) {
    req.setEncoding('utf8');
    req.body.mei = '';
    req.on('data', (data) => { req.body.mei += data; });
    req.on('end', () => { next(); });
  } else {
    next();
  }
};

//===========
// Bodyparser
//===========
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ limit: '50mb', extended: false }));
app.use(handleMEI);

//=====================
// Route import & setup
//=====================
app.use('/', routes);

//=====================
// Templating Engine
//=====================

app.set('views', 'deployment/views');
app.set('view engine', 'pug');

//=============
// Static Files
//=============
app.use(express.static('deployment/public'));

app.listen(8080);

console.log('Server hosted at :8080');
