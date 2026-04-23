const express = require('express');
const axios = require('axios');
const path = require('path');
const app = express();

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

const RHDH_URL = process.env.RHDH_URL;
const API_TOKEN = process.env.RHDH_TOKEN;

// Route: Web Front End
app.get('/', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head><title>Backstage Notifications</title></head>
        <body style="font-family: sans-serif; padding: 20px;">
            <h2>Send Backstage Notifications</h2>
            <form action="/send" method="POST">
                <p>Title:<br><input type="text" name="title" placeholder="System Alert" required></p>
                <p>Message:<br><textarea name="message" required></textarea></p>
                <p>Target User (optional):<br><input type="text" name="target" placeholder="user:default/guest"></p>
                <p>Severity:<br>
                    <select name="severity">
                        <option value="normal">Normal</option>
                        <option value="high">High</option>
                        <option value="low">Low</option>
                    </select>
                </p>
                <button type="submit" style="padding: 10px 20px; background: #0066cc; color: white; border: none; cursor: pointer;">
                    Push to Developer Hub
                </button>
            </form>
        </body>
        </html>
    `);
});

// Route: API Logic
app.post('/send', async (req, res) => {
    const { title, message, target, severity } = req.body;
    
    try {
        const response = await axios.post(`${RHDH_URL}/api/notifications/notifications`, {
            recipients: target ? { type: 'entity', entityRef: target } : { type: 'broadcast' },
            payload: {
                title: title,
                description: message,
                severity: severity,
                link: '/catalog' // Link where user goes when clicking notification
            }
        }, {
            headers: { 'Authorization': `Bearer ${API_TOKEN}` }
        });

        res.send('<h3>Notification Sent!</h3><a href="/">Send another</a>');
    } catch (error) {
        console.error('Error sending to RHDH:', error.message);
        res.status(500).send(`Failed: ${error.response?.data?.error || error.message}`);
    }
});

app.listen(3000, () => console.log('Server running on port 3000'));

