const express = require('express');
const request = require('request');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

app.get('/proxy', (req, res) => {
  const url = req.query.url;
  if (!url) return res.status(400).send('URL is required');

  request({
    url: url,
    method: 'GET',
    followAllRedirects: true
  }, (error, response, body) => {
    if (error || response.statusCode !== 200) {
      return res.status(500).send('Error fetching playlist: ' + (error ? error.message : 'Status ' + response.statusCode));
    }
    res.set('Content-Type', 'text/plain');
    res.send(body);
  });
});

app.listen(process.env.PORT || 3000, () => {
  console.log('Server running on port ' + (process.env.PORT || 3000));
});
