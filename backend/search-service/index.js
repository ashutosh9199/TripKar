const express = require('express');
const cors = require('cors');

const app = express();
const PORT = 5002;

app.use(cors());
app.use(express.json());

// Mock trips
const trips = [
  { id: '1', destination: 'Paris', price: 1200 },
  { id: '2', destination: 'Tokyo', price: 1500 },
  { id: '3', destination: 'New York', price: 1000 }
];

app.get('/api/search/trips', (req, res) => {
  const { query } = req.query;
  if (query) {
    return res.json(trips.filter(t => t.destination.toLowerCase().includes(query.toLowerCase())));
  }
  res.json(trips);
});

app.listen(PORT, () => {
  console.log(`Search Service is running on port ${PORT}`);
});
