/**
 * WhatsApp Watcher - Proper Implementation
 * Uses whatsapp-web.js library for reliable message monitoring
 */

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');

const VAULT_PATH = __dirname;
const NEEDS_ACTION = path.join(VAULT_PATH, 'Needs_Action');
const SEND_QUEUE = path.join(VAULT_PATH, 'Send_Queue');
const DONE = path.join(VAULT_PATH, 'Done');
const CONTACTS_TRACKER = path.join(VAULT_PATH, 'whatsapp_contacts_tracker.json');

// Create Send_Queue folder if it doesn't exist
if (!fs.existsSync(SEND_QUEUE)) {
    fs.mkdirSync(SEND_QUEUE, { recursive: true });
}

// Load or create contacts tracker
let contactsTracker = {};
if (fs.existsSync(CONTACTS_TRACKER)) {
    try {
        contactsTracker = JSON.parse(fs.readFileSync(CONTACTS_TRACKER, 'utf8'));
    } catch (error) {
        console.log('Creating new contacts tracker...');
        contactsTracker = {};
    }
}

// Save contacts tracker
function saveContactsTracker() {
    fs.writeFileSync(CONTACTS_TRACKER, JSON.stringify(contactsTracker, null, 2), 'utf8');
}

// Check if auto-reply should be sent (first time or after 3+ hours)
function shouldSendAutoReply(contactNumber) {
    const now = Date.now();
    const lastMessageTime = contactsTracker[contactNumber];

    if (!lastMessageTime) {
        // First time message
        return true;
    }

    const hoursSinceLastMessage = (now - lastMessageTime) / (1000 * 60 * 60);

    if (hoursSinceLastMessage >= 3) {
        // 3+ hours since last message
        return true;
    }

    return false;
}

// Initialize WhatsApp client with persistent session
const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: path.join(VAULT_PATH, 'whatsapp_session_js')
    }),
    puppeteer: {
        headless: false,
        args: ['--no-sandbox']
    }
});

// Track processed messages
const processedMessages = new Set();

// Process send queue
async function processSendQueue() {
    try {
        if (!fs.existsSync(SEND_QUEUE)) return;

        const queueFiles = fs.readdirSync(SEND_QUEUE).filter(f => f.endsWith('.md'));
        if (queueFiles.length === 0) return;

        for (const file of queueFiles) {
            try {
                const filePath = path.join(SEND_QUEUE, file);
                const content = fs.readFileSync(filePath, 'utf8');

                // Parse YAML frontmatter (handle both \n and \r\n line endings)
                const yamlMatch = content.match(/---[\r\n]+([\s\S]*?)[\r\n]+---/);
                if (!yamlMatch) {
                    console.log(`⚠️  Skipping ${file}: No YAML frontmatter found`);
                    console.log(`   Content preview: ${content.substring(0, 100)}`);
                    continue;
                }

                const yamlLines = yamlMatch[1].split('\n');
                let phoneNumber = '';
                let message = '';

                // Extract phone and message from YAML
                for (const line of yamlLines) {
                    if (line.startsWith('to:')) {
                        phoneNumber = line.replace('to:', '').trim();
                    }
                }

                // Extract message from body (after "## Message" or "## Drafted Response" or "## WhatsApp Message")
                // Handle both \n and \r\n line endings
                const messageMatch = content.match(/## (?:Message|Drafted Response|WhatsApp Message)[\r\n]+[\r\n]+([\s\S]*?)(?:[\r\n]+[\r\n]+##|$)/);
                if (messageMatch) {
                    message = messageMatch[1].trim();
                }

                if (!phoneNumber || !message) {
                    console.log(`⚠️  Skipping ${file}: Missing phone (${phoneNumber}) or message (${message ? 'found' : 'missing'})`);
                    continue;
                }

                // Format phone number
                let formattedNumber = phoneNumber.replace(/\s+/g, '');
                if (formattedNumber.startsWith('0')) {
                    formattedNumber = '92' + formattedNumber.substring(1);
                } else if (!formattedNumber.startsWith('92')) {
                    formattedNumber = '92' + formattedNumber;
                }
                formattedNumber = formattedNumber + '@c.us';

                console.log(`\n📤 Sending queued message...`);
                console.log(`   To: ${phoneNumber}`);
                console.log(`   Message: ${message.substring(0, 50)}...`);

                // Send message
                await client.sendMessage(formattedNumber, message);

                console.log(`✅ Message sent successfully!`);

                // Move to Done
                const doneFile = file.replace('.md', '_SENT.md');
                fs.renameSync(filePath, path.join(DONE, doneFile));
                console.log(`   Moved to Done/${doneFile}\n`);

            } catch (error) {
                console.error(`❌ Error sending ${file}:`, error.message);
            }
        }
    } catch (error) {
        console.error('❌ Queue processor error:', error.message);
    }
}

// Track processed messages

// QR Code for first-time authentication
client.on('qr', (qr) => {
    console.log('============================================================');
    console.log('WhatsApp Watcher - First Time Setup');
    console.log('============================================================');
    console.log('Scan this QR code with your phone:\n');
    qrcode.generate(qr, { small: true });
    console.log('\nWaiting for authentication...\n');
});

// Ready event
client.on('ready', () => {
    console.log('============================================================');
    console.log('WhatsApp Watcher Started');
    console.log('============================================================');
    console.log(`Vault: ${VAULT_PATH}`);
    console.log('Status: ✓ Connected and monitoring');
    console.log('Mode: Capturing ALL incoming messages');
    console.log('Queue: Checking Send_Queue every 5 seconds');
    console.log('\nPress Ctrl+C to stop\n');

    // Start queue processor
    setInterval(() => processSendQueue(), 5000);
});

// Message event - THIS IS THE KEY PART
client.on('message', async (message) => {
    try {
        // Get message details
        const contact = await message.getContact();
        const chat = await message.getChat();
        const messageBody = message.body;
        const timestamp = new Date(message.timestamp * 1000);

        // Skip if already processed
        const msgId = `${contact.id.user}_${message.id.id}`;
        if (processedMessages.has(msgId)) {
            return;
        }
        processedMessages.add(msgId);

        // Get contact name and number
        const contactName = contact.pushname || contact.name || contact.number;
        const contactNumber = contact.number;

        // Print to terminal
        console.log('\n📱 New WhatsApp message received!');
        console.log(`   From: ${contactName}`);
        console.log(`   Message: ${messageBody.substring(0, 100)}...`);
        console.log(`   Time: ${timestamp.toISOString()}`);

        // Check if auto-reply should be sent
        const sendAutoReply = shouldSendAutoReply(contactNumber);

        if (sendAutoReply) {
            console.log(`   🤖 Auto-reply: YES (first time or 3+ hours gap)`);

            // Create queue file for auto-reply
            const queueFilename = `QUEUE_autoreply_${contactNumber}_${Date.now()}.md`;
            const queueContent = `---
to: ${contactNumber}
contact: ${contactName}
queued_at: ${new Date().toISOString()}
type: auto_reply
---

# Queued WhatsApp Auto-Reply

## Contact

**Name:** ${contactName}
**Phone:** ${contactNumber}

## Drafted Response

Thank you for your message! Bashar will respond to you soon. Please wait a moment.
`;

            const queuePath = path.join(SEND_QUEUE, queueFilename);
            fs.writeFileSync(queuePath, queueContent, 'utf8');
            console.log(`   ✅ Auto-reply queued: ${queueFilename}`);
        } else {
            console.log(`   🤖 Auto-reply: NO (recent conversation)`);
        }

        // Update last message time for this contact
        contactsTracker[contactNumber] = Date.now();
        saveContactsTracker();

        // Create task file
        const taskContent = `---
type: whatsapp
from: ${contactName}
phone: ${contactNumber}
received: ${timestamp.toISOString()}
priority: normal
status: pending
auto_reply_sent: ${sendAutoReply}
---

# WhatsApp Message from ${contactName}

## Message Content

${messageBody}

## Contact Details

- Name: ${contactName}
- Phone: ${contactNumber}
- Chat: ${chat.name || 'Direct Message'}

## Suggested Actions

- [ ] Reply to contact
- [ ] Take requested action
- [ ] Mark as complete

## Instructions

New WhatsApp message received. Analyze and respond appropriately.
If reply needed, draft it and request approval before sending.
`;

        // Save to Needs_Action
        const safeContactName = contactName.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 30);
        const taskFilename = `WHATSAPP_${safeContactName}_${Date.now()}.md`;
        const taskPath = path.join(NEEDS_ACTION, taskFilename);

        fs.writeFileSync(taskPath, taskContent, 'utf8');

        console.log(`✅ Task created: ${taskFilename}`);
        console.log(`   Location: Needs_Action/${taskFilename}\n`);

    } catch (error) {
        console.error('❌ Error processing message:', error);
    }
});

// Error handling
client.on('auth_failure', () => {
    console.error('❌ Authentication failed. Delete whatsapp_session_js folder and try again.');
});

client.on('disconnected', (reason) => {
    console.log('⚠ WhatsApp disconnected:', reason);
    console.log('Attempting to reconnect...');
});

// Start the client
console.log('Initializing WhatsApp client...');
client.initialize();

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('\n\n✓ Shutting down WhatsApp watcher...');
    await client.destroy();
    console.log('✓ Disconnected from WhatsApp');
    process.exit(0);
});
