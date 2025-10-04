// server.js - Express Authentication Backend
const express = require('express');
const session = require('express-session');
const cors = require('cors');
const bcrypt = require('bcrypt');
const { google } = require('googleapis');
const multer = require('multer');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(express.json());
app.use(cors({
    origin: 'http://localhost:8501', // Streamlit default port
    credentials: true
}));

// Session configuration
app.use(session({
    secret: process.env.SESSION_SECRET || 'your-secret-key-change-in-production',
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: false, // Set to true in production with HTTPS
        httpOnly: true,
        maxAge: 24 * 60 * 60 * 1000 // 24 hours
    }
}));

// In-memory user storage (replace with database in production)
const users = new Map();

// Google Drive OAuth2 configuration
const oauth2Client = new google.auth.OAuth2(
    process.env.GOOGLE_CLIENT_ID,
    process.env.GOOGLE_CLIENT_SECRET,
    process.env.GOOGLE_REDIRECT_URI || 'http://localhost:5000/auth/google/callback'
);

// Middleware to check authentication
const isAuthenticated = (req, res, next) => {
    if (req.session.userId) {
        next();
    } else {
        res.status(401).json({ error: 'Not authenticated' });
    }
};

// ============= AUTH ROUTES =============

// Register
app.post('/api/auth/register', async (req, res) => {
    try {
        const { email, password, name } = req.body;

        if (!email || !password || !name) {
            return res.status(400).json({ error: 'All fields required' });
        }

        if (users.has(email)) {
            return res.status(400).json({ error: 'User already exists' });
        }

        // Hash password
        const hashedPassword = await bcrypt.hash(password, 10);

        // Store user
        users.set(email, {
            email,
            password: hashedPassword,
            name,
            createdAt: new Date(),
            googleDriveConnected: false
        });

        res.json({ 
            success: true, 
            message: 'Registration successful',
            user: { email, name }
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Login
app.post('/api/auth/login', async (req, res) => {
    try {
        const { email, password } = req.body;

        if (!email || !password) {
            return res.status(400).json({ error: 'Email and password required' });
        }

        const user = users.get(email);
        
        if (!user) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }

        // Verify password
        const isValidPassword = await bcrypt.compare(password, user.password);
        
        if (!isValidPassword) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }

        // Set session
        req.session.userId = email;
        req.session.userName = user.name;

        res.json({ 
            success: true,
            user: {
                email: user.email,
                name: user.name,
                googleDriveConnected: user.googleDriveConnected
            }
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Logout
app.post('/api/auth/logout', (req, res) => {
    req.session.destroy((err) => {
        if (err) {
            return res.status(500).json({ error: 'Logout failed' });
        }
        res.json({ success: true, message: 'Logged out successfully' });
    });
});

// Check auth status
app.get('/api/auth/status', (req, res) => {
    if (req.session.userId) {
        const user = users.get(req.session.userId);
        res.json({ 
            authenticated: true,
            user: {
                email: user.email,
                name: user.name,
                googleDriveConnected: user.googleDriveConnected
            }
        });
    } else {
        res.json({ authenticated: false });
    }
});

// ============= GOOGLE DRIVE INTEGRATION =============

// Initiate Google Drive authorization
app.get('/api/drive/authorize', isAuthenticated, (req, res) => {
    const authUrl = oauth2Client.generateAuthUrl({
        access_type: 'offline',
        scope: [
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/drive.metadata.readonly'
        ],
        state: req.session.userId // Pass user ID for callback
    });
    
    res.json({ authUrl });
});

// Google OAuth callback
app.get('/auth/google/callback', async (req, res) => {
    try {
        const { code, state } = req.query;
        const userId = state;

        // Exchange code for tokens
        const { tokens } = await oauth2Client.getToken(code);
        
        // Store tokens for user
        const user = users.get(userId);
        if (user) {
            user.googleDriveTokens = tokens;
            user.googleDriveConnected = true;
            users.set(userId, user);
        }

        res.send(`
            <html>
                <body>
                    <h2>Google Drive Connected Successfully!</h2>
                    <p>You can close this window and return to the app.</p>
                    <script>
                        setTimeout(() => window.close(), 2000);
                    </script>
                </body>
            </html>
        `);
    } catch (error) {
        res.status(500).send('Authorization failed: ' + error.message);
    }
});

// List screenshots from Google Drive
app.get('/api/drive/screenshots', isAuthenticated, async (req, res) => {
    try {
        const user = users.get(req.session.userId);
        
        if (!user.googleDriveConnected || !user.googleDriveTokens) {
            return res.status(400).json({ error: 'Google Drive not connected' });
        }

        oauth2Client.setCredentials(user.googleDriveTokens);
        const drive = google.drive({ version: 'v3', auth: oauth2Client });

        // Search for image files (screenshots)
        const response = await drive.files.list({
            q: "mimeType contains 'image/' and trashed=false",
            fields: 'files(id, name, mimeType, createdTime, thumbnailLink, webViewLink)',
            pageSize: 100,
            orderBy: 'createdTime desc'
        });

        res.json({ 
            success: true,
            files: response.data.files 
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Download specific file from Google Drive
app.get('/api/drive/download/:fileId', isAuthenticated, async (req, res) => {
    try {
        const user = users.get(req.session.userId);
        
        if (!user.googleDriveConnected || !user.googleDriveTokens) {
            return res.status(400).json({ error: 'Google Drive not connected' });
        }

        oauth2Client.setCredentials(user.googleDriveTokens);
        const drive = google.drive({ version: 'v3', auth: oauth2Client });

        const { fileId } = req.params;

        // Get file metadata
        const metadata = await drive.files.get({
            fileId: fileId,
            fields: 'name, mimeType'
        });

        // Download file
        const response = await drive.files.get(
            { fileId: fileId, alt: 'media' },
            { responseType: 'arraybuffer' }
        );

        // Send file
        res.set('Content-Type', metadata.data.mimeType);
        res.set('Content-Disposition', `attachment; filename="${metadata.data.name}"`);
        res.send(Buffer.from(response.data));
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Disconnect Google Drive
app.post('/api/drive/disconnect', isAuthenticated, (req, res) => {
    try {
        const user = users.get(req.session.userId);
        if (user) {
            user.googleDriveTokens = null;
            user.googleDriveConnected = false;
            users.set(req.session.userId, user);
        }
        res.json({ success: true, message: 'Google Drive disconnected' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// ============= USER PROFILE =============

app.get('/api/user/profile', isAuthenticated, (req, res) => {
    const user = users.get(req.session.userId);
    res.json({
        email: user.email,
        name: user.name,
        googleDriveConnected: user.googleDriveConnected,
        createdAt: user.createdAt
    });
});

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date() });
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Server running on http://localhost:${PORT}`);
    console.log(`📊 Streamlit should be on http://localhost:8501`);
});

module.exports = app;