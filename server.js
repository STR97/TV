const express = require('express');
const request = require('request');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

// Прокси для загрузки плейлиста
app.get('/proxy', (req, res) => {
  const url = req.query.url;
  const username = req.query.username;
  const password = req.query.password;
  if (!url) return res.status(400).send('URL is required');

  request({
    url: url,
    method: 'GET',
    followAllRedirects: true,
    auth: username && password ? { user: username, pass: password } : undefined,
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
  }, (error, response, body) => {
    if (error || response.statusCode !== 200) {
      return res.status(500).send('Error fetching playlist: ' + (error ? error.message : 'Status ' + response.statusCode));
    }
    res.set('Content-Type', 'text/plain');
    res.send(body);
  });
});

// Прокси для воспроизведения каналов
app.get('/stream', (req, res) => {
  const url = req.query.url;
  const token = req.query.token;
  if (!url) return res.status(400).send('URL is required');

  const options = {
    url: url,
    method: 'GET',
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Referer': 'https://tv-cyan-pi.vercel.app'
    }
  };

  request(options)
    .on('response', (response) => {
      if (response.statusCode !== 200) {
        res.status(response.statusCode).send('Stream error: Status ' + response.statusCode);
      }
    })
    .on('error', (err) => {
      res.status(500).send('Error streaming: ' + err.message);
    })
    .pipe(res);
});

app.listen(process.env.PORT || 3000, () => {
  console.log('Server running on port ' + (process.env.PORT || 3000));
});
