var express = require('express');
var router = express.Router();
var DatabaseConnector = require('./../DatabaseConnector');

router.get('/', function (req, res) {
  res.render('pages/index');
});

router.get('/api/analogValues', function(req, res){
  DatabaseConnector.selectAnalogValues(req.query.dingroup, req.query.value, req.query.dateStart, req.query.dateEnd).then(result => {
    console.log("sending result");
    res.json(result);
  });
});

module.exports = router;
