# Telegram Setup Guide

Step-by-step guide to configure Telegram notifications for the Face Security Alert System.

## Why Telegram?

- ✅ Free unlimited notifications
- ✅ Instant delivery worldwide
- ✅ Photo attachments supported
- ✅ Works on all devices
- ✅ No SMS costs
- ✅ Reliable and secure

---

## Setup Steps

### Step 1: Create a Telegram Bot

1. **Open Telegram** on your phone or computer

2. **Search for BotFather**
   - In Telegram search: `@BotFather`
   - Or visit: https://t.me/botfather

3. **Start a chat with BotFather**
   - Click "Start" or send `/start`

4. **Create a new bot**
   - Send command: `/newbot`
   
5. **Choose a name for your bot**
   - Example: `My Home Security Bot`
   - This is the display name users will see

6. **Choose a username for your bot**
   - Must end in `bot`
   - Example: `my_home_security_bot`
   - Must be unique

7. **Save your bot token**
   - BotFather will send you a token like:
     ```
     1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
     ```
   - **Keep this secret!** Anyone with this token can control your bot

8. **Optional: Set bot description and profile picture**
   - `/setdescription` - Add description
   - `/setuserpic` - Add profile picture

### Step 2: Get Your Chat ID

Method 1: Using userinfobot (Easiest)

1. **Search for userinfobot**
   - In Telegram search: `@userinfobot`
   - Or visit: https://t.me/userinfobot

2. **Start a chat**
   - Click "Start" or send `/start`

3. **Copy your Chat ID**
   - Bot will show: `Id: 123456789`
   - This is your chat ID

Method 2: Using your bot

1. **Find your bot**
   - Search for your bot's username
   - Example: `@my_home_security_bot`

2. **Start a chat**
   - Click "Start"
   - Send any message (like "Hello")

3. **Get updates via web**
   - Open this URL in browser (replace YOUR_BOT_TOKEN):
     ```
     https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
     ```
   
4. **Find your chat ID**
   - Look for `"chat":{"id":123456789`
   - The number is your chat ID

### Step 3: Configure the System

1. **Copy the example environment file**
   ```bash
   copy .env.example .env
   ```

2. **Edit `.env` file**
   - Open with Notepad or any text editor
   - Add your credentials:
   ```
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_CHAT_ID=123456789
   ```

3. **Save the file**

4. **Verify configuration**
   ```bash
   python -c "from config import TELEGRAM_CONFIG; print('Bot Token:', '✓' if TELEGRAM_CONFIG['bot_token'] else '✗'); print('Chat ID:', '✓' if TELEGRAM_CONFIG['chat_id'] else '✗')"
   ```

### Step 4: Test the Connection

**Using Python**:

```python
from src.alert_system import AlertSystem
from config import TELEGRAM_CONFIG, ALERT_CONFIG

alert_system = AlertSystem(
    telegram_bot_token=TELEGRAM_CONFIG['bot_token'],
    telegram_chat_id=TELEGRAM_CONFIG['chat_id'],
    enable_telegram=True,
    enable_desktop=False,
    save_unknown_faces=False,
    unknown_faces_dir=ALERT_CONFIG['unknown_faces_dir']
)

# Test connection
if alert_system.test_telegram_connection():
    print("✅ Telegram is working!")
else:
    print("❌ Telegram connection failed")
```

**Using Jupyter Notebook**:

Open `notebooks/01_setup_and_testing.ipynb` and run the Telegram test cell.

---

## Troubleshooting

### Issue 1: "Unauthorized" Error

**Cause**: Incorrect bot token

**Solution**:
1. Verify token from BotFather
2. Make sure no extra spaces in `.env`
3. Token should be one continuous string

### Issue 2: "Chat Not Found" Error

**Cause**: Incorrect chat ID or bot not started

**Solution**:
1. Make sure you started a chat with your bot
2. Send at least one message to the bot
3. Verify chat ID using getUpdates method

### Issue 3: No Messages Received

**Cause**: Bot might be blocked or chat ID wrong

**Solution**:
1. Check if bot is blocked in Telegram
2. Verify chat ID is correct number (no quotes needed)
3. Try sending a test message via browser:
   ```
   https://api.telegram.org/botYOUR_TOKEN/sendMessage?chat_id=YOUR_CHAT_ID&text=Test
   ```

### Issue 4: "Connection Timeout"

**Cause**: Internet connectivity issue

**Solution**:
1. Check internet connection
2. Check firewall settings
3. Try using VPN if Telegram is blocked

### Issue 5: Photos Not Sending

**Cause**: File size or format issue

**Solution**:
1. Verify photo file exists
2. Check file size (max 10MB for Telegram)
3. Ensure file format is supported (JPG, PNG)

---

## Advanced Configuration

### Custom Message Template

Edit `config.py`:

```python
TELEGRAM_CONFIG = {
    "message_template": """
    🚨 *SECURITY ALERT* 🚨
    
    Unknown person detected!
    
    📅 Date: {timestamp}
    📊 Confidence: {confidence}%
    📍 Location: Home Entry
    
    Please check the attached photo.
    """,
}
```

### Multiple Recipients

To send to multiple people/groups:

1. **Create a Telegram group**
2. **Add your bot to the group**
3. **Make bot an admin** (optional)
4. **Get group chat ID**
   - Send message in group
   - Use getUpdates method
   - Look for negative number (like `-123456789`)
5. **Update `.env`**:
   ```
   TELEGRAM_CHAT_ID=-123456789
   ```

### Rich Formatting

Telegram supports Markdown and HTML:

```python
# Markdown
message = """
*Bold text*
_Italic text_
`Code text`
[Link](http://example.com)
"""

# HTML
message = """
<b>Bold text</b>
<i>Italic text</i>
<code>Code text</code>
<a href="http://example.com">Link</a>
"""
```

### Alert Rate Limiting

Prevent too many alerts:

```python
ALERT_CONFIG = {
    "max_alerts_per_hour": 20,  # Maximum 20 alerts per hour
    "cooldown_seconds": 30,     # Minimum 30s between alerts
}
```

---

## Best Practices

### Security

1. **Never share your bot token**
   - Don't commit to public repositories
   - `.env` is in `.gitignore` by default

2. **Use bot only for your chat**
   - Don't add bot to public groups
   - Monitor bot usage

3. **Regenerate token if compromised**
   - Use `/revoke` in BotFather
   - Update `.env` with new token

### Privacy

1. **Disable bot commands** (optional)
   - `/setcommands` in BotFather
   - Set to empty list

2. **Disable group privacy** if needed
   - `/setprivacy` in BotFather
   - Choose "Disable"

### Reliability

1. **Test regularly**
   - Send test alerts weekly
   - Verify photos are received

2. **Monitor bot status**
   - Check if bot is online
   - Look for error messages

3. **Have backup notification**
   - Keep desktop notifications enabled
   - Consider SMS backup service

---

## Alternative: Telegram Channels

For broadcasting to many users:

1. **Create a Telegram Channel**
2. **Make your bot an admin**
3. **Get channel ID**
   - Format: `@channel_username` or `-100123456789`
4. **Update chat ID in `.env`**

---

## Testing Checklist

- [ ] Bot created with BotFather
- [ ] Bot token saved in `.env`
- [ ] Chat started with bot
- [ ] Chat ID saved in `.env`
- [ ] Test message received
- [ ] Test photo received
- [ ] Alerts working in security system

---

## Additional Resources

- **Telegram Bot API**: https://core.telegram.org/bots/api
- **BotFather Commands**: https://core.telegram.org/bots#6-botfather
- **Telegram Bot Tutorial**: https://core.telegram.org/bots/tutorial

---

## Getting Help

If you're still having issues:

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review Telegram Bot API documentation
3. Verify `.env` file format
4. Test with curl:
   ```bash
   curl "https://api.telegram.org/botYOUR_TOKEN/getMe"
   ```

---

**Setup complete?** → Continue to [USAGE.md](USAGE.md)
