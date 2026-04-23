const express = require('express');
const cors = require('cors');

const app = express();
const PORT = 5004;

app.use(cors());
app.use(express.json());

app.post('/api/payments/process', (req, res) => {
  const { bookingId, amount, paymentMethod } = req.body;
  // Mock payment processing
  const success = Math.random() > 0.1; // 90% success rate
  if (success) {
    res.json({ status: 'success', transactionId: Date.now().toString() });
  } else {
    res.status(400).json({ status: 'failed', message: 'Payment declined' });
  }
});

app.listen(PORT, () => {
  console.log(`Payment Service is running on port ${PORT}`);
});
