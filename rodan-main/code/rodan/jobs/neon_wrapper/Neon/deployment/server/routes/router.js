var express = require('express');

var router = express.Router();

router.use('/dish', require('./index'));

module.exports = router;
