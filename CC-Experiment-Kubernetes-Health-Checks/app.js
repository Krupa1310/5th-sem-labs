
const express = require('express');

const app = express();

let live = true;
let ready = true;

app.get('/', (req, res) => {
    res.send('Kubernetes Health Check Application is Running!');
});

app.get('/live', (req, res) => {
    if (live) {
        res.status(200).send('Application is Alive');
    } else {
        res.status(500).send('Application is Not Alive');
    }
});

app.get('/ready', (req, res) => {
    if (ready) {
        res.status(200).send('Application is Ready');
    } else {
        res.status(500).send('Application is Not Ready');
    }
});

app.get('/fail-live', (req, res) => {
    live = false;
    res.send('Liveness failure simulated');
});

app.get('/not-ready', (req, res) => {
    ready = false;
    res.send('Readiness failure simulated');
});

app.get('/recover', (req, res) => {
    ready = true;
    res.send('Application is Ready Again');
});

app.listen(3000, '0.0.0.0', () => {
    console.log('Application running on port 3000');
});
