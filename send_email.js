const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');

const CREDENTIALS_PATH = path.join(__dirname, 'credentials.json');
const TOKEN_PATH = path.join(__dirname, 'gmail_token.json');

async function sendEmail(to, subject, body) {
    try {
        // Load credentials
        const credentials = JSON.parse(fs.readFileSync(CREDENTIALS_PATH));
        const { client_secret, client_id, redirect_uris } = credentials.installed || credentials.web;

        const oAuth2Client = new google.auth.OAuth2(
            client_id,
            client_secret,
            redirect_uris[0]
        );

        // Load token
        let token = JSON.parse(fs.readFileSync(TOKEN_PATH));
        oAuth2Client.setCredentials(token);

        const gmail = google.gmail({ version: 'v1', auth: oAuth2Client });

        // Try to send, if token expired, refresh and retry
        try {
            return await sendWithGmail(gmail, to, subject, body);
        } catch (error) {
            if (error.message.includes('invalid_grant') || error.message.includes('Token has been expired')) {
                console.log('⚠️  Token expired, attempting refresh...');
                
                try {
                    // Refresh the token
                    const refreshResponse = await oAuth2Client.refreshToken(token.refresh_token);
                    const newToken = refreshResponse.credentials;
                    
                    // Save new token
                    fs.writeFileSync(TOKEN_PATH, JSON.stringify(newToken));
                    console.log('✅ Token refreshed and saved!');
                    
                    // Set new credentials and retry
                    oAuth2Client.setCredentials(newToken);
                    return await sendWithGmail(gmail, to, subject, body);
                } catch (refreshError) {
                    console.log('❌ Token refresh failed. Token may be revoked.');
                    console.log('');
                    console.log('🔐 TO FIX: Re-authenticate by running:');
                    console.log('   python gmail_watcher.py');
                    console.log('');
                    console.log('This will open a browser for you to login again.');
                    throw new Error('Token expired. Please re-authenticate.');
                }
            }
            throw error;
        }

    } catch (error) {
        console.error('❌ Failed to send email:', error.message);
        return {
            success: false,
            error: error.message
        };
    }
}

async function sendWithGmail(gmail, to, subject, body) {
    // Create email
    const message = [
        `To: ${to}`,
        `Subject: ${subject}`,
        'Content-Type: text/plain; charset=utf-8',
        '',
        body
    ].join('\n');

    const encodedMessage = Buffer.from(message)
        .toString('base64')
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '');

    // Send
    const result = await gmail.users.messages.send({
        userId: 'me',
        requestBody: { raw: encodedMessage }
    });

    console.log('✅ Email sent successfully!');
    console.log(`   To: ${to}`);
    console.log(`   Subject: ${subject}`);
    console.log(`   Message ID: ${result.data.id}`);

    return {
        success: true,
        messageId: result.data.id,
        sentAt: new Date().toISOString()
    };
}

// Command line interface
if (require.main === module) {
    const args = process.argv.slice(2);

    // Support reading from temp file (avoids command line escaping issues)
    if (args[0] === '--from-file' && args[1]) {
        const fs = require('fs');
        const emailData = JSON.parse(fs.readFileSync(args[1], 'utf8'));
        
        sendEmail(emailData.to, emailData.subject, emailData.body)
            .then(result => {
                if (result.success) {
                    process.exit(0);
                } else {
                    process.exit(1);
                }
            });
        return;
    }

    // Legacy command line mode
    if (args.length < 3) {
        console.log('Usage: node send_email.js <to> <subject> <body>');
        console.log('   or: node send_email.js --from-file <temp_file.json>');
        console.log('Example: node send_email.js user@example.com "Test Subject" "Email body"');
        process.exit(1);
    }

    const [to, subject, body] = args;

    sendEmail(to, subject, body)
        .then(result => {
            if (result.success) {
                process.exit(0);
            } else {
                process.exit(1);
            }
        });
}

module.exports = { sendEmail };

// node send_email.js "bashartc14@gmail.com" "Test from AI Employee" "This should work now!"