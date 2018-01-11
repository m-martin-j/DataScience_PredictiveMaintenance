var express = require('express');
var router = express.Router();
var DatabaseConnector = require('./../DatabaseConnector');

router.get('/', function (req, res) {
  res.render('pages/index');
});

router.get('/warnings', function (req, res) {
  res.render('pages/warnings');
});

router.get('/results', function (req, res) {
  res.render('pages/results');
});

router.get('/api/analogValues', function(req, res){
  DatabaseConnector.selectAnalogValues(req.query.dingroup, req.query.value, req.query.dateStart, req.query.dateEnd, req.query.includeZeros).then(result => {
    console.log("sending result");
    res.json(result);
  });
});

router.get('/api/warnings', function(req, res){
  DatabaseConnector.selectWarnings(req.query.includeInfos, req.query.includeWarnings, req.query.includeErrors, req.query.dateStart, req.query.dateEnd).then(result => {
    console.log("sending result");
    res.json(result);
  });
});

module.exports = router;
