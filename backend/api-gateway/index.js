const express = require('express');
const cors = require('cors');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = 5000;

app.use(cors());

// Proxy endpoints
app.use('/api/users', createProxyMiddleware({ target: 'http://localhost:5001', changeOrigin: true }));
app.use('/api/search', createProxyMiddleware({ target: 'http://localhost:5002', changeOrigin: true }));
app.use('/api/bookings', createProxyMiddleware({ target: 'http://localhost:5003', changeOrigin: true }));
app.use('/api/payments', createProxyMiddleware({ target: 'http://localhost:5004', changeOrigin: true }));
app.use('/api/notifications', createProxyMiddleware({ target: 'http://localhost:5005', changeOrigin: true }));

app.listen(PORT, () => {
  console.log(`API Gateway is running on port ${PORT}`);
});
