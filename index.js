var express = require('express');
var app = express();

var YeelightBlue = require('yeelight-blue');
var discoveredYeelight = null;
var log = [];

function reconnect() {
    YeelightBlue.discover(function(yeelightBlue) {
        yeelightBlue.connectAndSetup(function() {
            discoveredYeelight = yeelightBlue;
            log.push('device reconnected');
            console.log('reconnect');
        });
        yeelightBlue.on('disconnect', function() {
            reconnect();
        });
    });
}

var server = app.listen(8080, function() {
    YeelightBlue.discover(function(yeelightBlue) {
        yeelightBlue.connectAndSetup(function() {
            discoveredYeelight = yeelightBlue;
            log.push('device reconnected');
            console.log('reconnect');
        });
        yeelightBlue.on('disconnect', function() {
            reconnect();
        });
    });
});

app.get('/disconnect', function(request, response) {
    discoveredYeelight.disconnect(function() {
        log.push('device disconnected');
        response.send(log.join('<br>'));
    });
});

app.get('/on', function(request, response) {
    discoveredYeelight.turnOn(function() {
        log.push('device on');
        response.send(log.join('<br>'));
    });
});

app.get('/off', function(request, response) {
    discoveredYeelight.turnOff(function() {
        log.push('device off');
        response.send(log.join('<br>'));
    });
});

app.get('/color', function(request, response) {
    var red = getIntRandom(0, 255);
    var green = getIntRandom(0, 255);
    var blue = getIntRandom(0, 255);
    var brightness = getIntRandom(0, 255);
    discoveredYeelight.setColorAndBrightness(red, green, blue, brightness, function() {
        log.push('color setted');
        //response.send(log.join('<br>'));
    });
    response.send(log.join('<br>'));
});

app.get('/log', function(request, response) {
    response.send(log.join('<br>'));
});

function getIntRandom(min, max) {
    return Math.floor(Math.random() * (max - min)) + min;
}