const { Client } = require('whatsapp-web.js');
const fs = require('fs');
const path = require('path');

const SESSION_PATH = path.join(__dirname, 'whatsapp_session_js');

async function sendWhatsAppMessage(phoneNumber, message) {
    try {
        console.log('Initializing WhatsApp client...');

        const client = new Client({
            authStrategy: new (require('whatsapp-web.js').LocalAuth)({
                dataPath: SESSION_PATH
            }),
            puppeteer: {
                headless: true,
                args: ['--no-sandbox']
            }
        });

        // Wait for client to be ready
        await new Promise((resolve, reject) => {
            client.on('ready', () => {
                console.log('✓ WhatsApp client ready');
                resolve();
            });

            client.on('auth_failure', () => {
                reject(new Error('Authentication failed'));
            });

            setTimeout(() => {
                reject(new Error('Timeout waiting for WhatsApp'));
            }, 60000);

            client.initialize();
        });

        // Format phone number (remove spaces, add country code if needed)
        let formattedNumber = phoneNumber.replace(/\s+/g, '');

        // If doesn't start with country code, assume Pakistan (+92)
        if (!formattedNumber.startsWith('+')) {
            if (formattedNumber.startsWith('0')) {
                // Local format: 03001234567 → +923001234567
                formattedNumber = '+92' + formattedNumber.substring(1);
            } else if (formattedNumber.startsWith('92')) {
                // Already has country code: 923001234567 → +923001234567
                formattedNumber = '+' + formattedNumber;
            } else {
                // Unknown format, assume needs country code
                formattedNumber = '+92' + formattedNumber;
            }
        }

        // Remove + for WhatsApp format
        formattedNumber = formattedNumber.replace('+', '') + '@c.us';

        console.log(`Sending message to: ${formattedNumber}`);

        // Send message
        await client.sendMessage(formattedNumber, message);

        console.log('✅ WhatsApp message sent successfully!');
        console.log(`   To: ${phoneNumber}`);
        console.log(`   Message: ${message.substring(0, 50)}...`);

        // Close client
        await client.destroy();

        return {
            success: true,
            to: phoneNumber,
            message: message,
            sentAt: new Date().toISOString()
        };

    } catch (error) {
        console.error('❌ Failed to send WhatsApp message:', error.message);
        return {
            success: false,
            error: error.message
        };
    }
}

// Command line interface
if (require.main === module) {
    const args = process.argv.slice(2);

    if (args.length < 2) {
        console.log('Usage: node send_whatsapp.js <phone_number> <message>');
        console.log('Example: node send_whatsapp.js "923001234567" "Hello from AI Employee"');
        console.log('Example: node send_whatsapp.js "03001234567" "Test message"');
        process.exit(1);
    }

    const [phoneNumber, message] = args;

    sendWhatsAppMessage(phoneNumber, message)
        .then(result => {
            if (result.success) {
                process.exit(0);
            } else {
                process.exit(1);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            process.exit(1);
        });
}

module.exports = { sendWhatsAppMessage };
