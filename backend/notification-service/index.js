const express = require('express');
const cors = require('cors');

const app = express();
const PORT = 5005;

app.use(cors());
app.use(express.json());

app.post('/api/notifications/send', (req, res) => {
  const { userId, type, message } = req.body;
  // Mock sending notification
  console.log(`Sending ${type} to user ${userId}: ${message}`);
  res.json({ status: 'sent', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`Notification Service is running on port ${PORT}`);
});
