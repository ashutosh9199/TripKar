const express = require('express');
const cors = require('cors');

const app = express();
const PORT = 5003;

app.use(cors());
app.use(express.json());

const bookings = [];

app.post('/api/bookings/create', (req, res) => {
  const { userId, tripId, passengers } = req.body;
  const newBooking = { id: Date.now().toString(), userId, tripId, passengers, status: 'pending' };
  bookings.push(newBooking);
  
  // Try to notify payment service, but keep simple for now
  res.status(201).json(newBooking);
});

app.get('/api/bookings/my-bookings/:userId', (req, res) => {
  const { userId } = req.params;
  const userBookings = bookings.filter(b => b.userId === userId);
  res.json(userBookings);
});

app.listen(PORT, () => {
  console.log(`Booking Service is running on port ${PORT}`);
});
