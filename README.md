# Telegram Publisher Bot

A secure and feature-rich Telegram bot for publishing messages to multiple groups with anti-ban measures and automated scheduling.

## 🚀 Features

- **Multi-Group Publishing**: Send messages to multiple Telegram groups simultaneously
- **Force Mode**: Automated continuous publishing with session auto-detection
- **Anti-Ban Protection**: Built-in rate limiting, random delays, and flood protection
- **Message Scheduling**: Configurable delays between messages (default 5 minutes)
- **Daily Limits**: Configurable daily message limits per group
- **Session Management**: Automatic session file detection and management
- **Error Handling**: Comprehensive error handling for network issues and API limits
- **Interactive Setup**: User-friendly setup wizard for first-time configuration

## 📋 Requirements

- Python 3.7+
- Telegram API credentials (API ID and API Hash)
- Active Telegram account

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/MyCato/Tpublish.git
   cd Tpublish
   ```

2. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```
   
   Or run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Get Telegram API credentials**:
   - Go to [https://my.telegram.org](https://my.telegram.org)
   - Log in with your phone number
   - Go to "API development tools"
   - Create a new application to get your `API ID` and `API Hash`

## 🚀 Quick Start

### First Time Setup (Interactive Mode)

```bash
python3 main.py
```

Follow the setup wizard to:
1. Enter your API credentials
2. Authenticate with your phone number
3. Add Telegram groups
4. Configure messages and delays

### Automated Mode (Force Mode)

For continuous automated publishing:

```bash
python3 main.py --force
```

**Requirements for Force Mode**:
- Existing `api_config.json` file
- At least one `.session` file in the directory
- Configured groups and messages

## 📖 Usage

### Available Commands

```bash
# Interactive mode (guided setup)
python3 main.py

# Force mode (automated continuous publishing)
python3 main.py --force

# Show help
python3 main.py --help
```

### Main Menu Options

1. **🚀 Start Publishing** - Begin sending messages to all configured groups
2. **➕ Add Groups** - Add new Telegram groups by chat ID
3. **➖ Remove Groups** - Remove groups from the publishing list
4. **✏️ Edit Messages & Delays** - Configure messages and timing
5. **⏹️ Stop & Exit** - Exit the application

### Configuration Options

- **Messages**: Set multiple messages to be sent sequentially
- **Delays**: Configure delays before each message (default: 300 seconds)
- **Daily Limits**: Set maximum messages per day per group (default: 50)
- **Anti-Ban Settings**: Automatic delays between groups (10-60 seconds)

## 🔒 Security Features

### Anti-Ban Protection
- **Rate Limiting**: Daily message limits per group
- **Random Delays**: Random intervals between groups (10-60 seconds)
- **Flood Protection**: Automatic handling of Telegram flood limits
- **Error Recovery**: Continues operation even if some groups fail

### Force Mode Safety
- **Tripled Rate Limits**: More lenient limits for automated usage
- **Light Delays**: 2-second intervals between groups
- **Continuous Monitoring**: Real-time status updates and error reporting

## 📁 File Structure

```
Tpublish/
├── main.py              # Main application
├── requirements.txt     # Python dependencies
├── setup.sh            # Automated setup script
├── README.md           # This file
├── LICENSE             # MIT License
├── .gitignore          # Git ignore rules
├── api_config.json     # API credentials (created during setup)
├── groups.json         # Groups list (created during setup)
├── config.json         # Messages and settings (created during setup)
└── *.session          # Telegram session files (created during setup)
```

## ⚙️ Configuration Files

### api_config.json
```json
{
  "api_id": 12345678,
  "api_hash": "your_api_hash_here",
  "phone": "+1234567890"
}
```

### config.json
```json
{
  "messages": ["Your message content here"],
  "delays": [300],
  "min_delay": 10,
  "max_delay": 60,
  "daily_limit": 50,
  "last_sent": {}
}
```

### groups.json
```json
[
  {
    "chat_id": "-1001234567890",
    "name": "Group Name",
    "added_date": "2024-01-01T12:00:00"
  }
]
```

## 🔧 Getting Group Chat IDs

### Method 1: Using @getidsbot
1. Add @getidsbot to your group
2. Send `/start` to the bot
3. The bot will reply with the group's chat ID

### Method 2: Using Web Telegram
1. Open [web.telegram.org](https://web.telegram.org)
2. Open the group chat
3. Look at the URL: `https://web.telegram.org/a/#-1001234567890`
4. The number after `#` is your chat ID

### Method 3: Using @userinfobot
1. Forward any message from the group to @userinfobot
2. The bot will show you the chat information including ID

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

- **Use Responsibly**: This bot is for legitimate broadcasting purposes only
- **Respect Telegram ToS**: Ensure your usage complies with Telegram's Terms of Service
- **Rate Limits**: Built-in protections help prevent bans, but excessive usage may still result in restrictions
- **Group Permissions**: Ensure you have permission to send messages to all target groups
- **Content Compliance**: You are responsible for the content of messages sent through this bot

## 🆘 Troubleshooting

### Common Issues

**"No module named 'telethon'"**
```bash
pip3 install telethon
```

**"Force mode requires existing API configuration"**
- Run `python3 main.py` first to complete initial setup

**"Daily limit reached"**
- Wait 24 hours or increase the daily limit in settings

**"Flood wait error"**
- The bot automatically handles this, just wait for the specified time

**Session file not found**
- Complete the authentication process in interactive mode first

### Getting Help

- Check the [Issues](https://github.com/MyCato/Tpublish/issues) page
- Create a new issue with detailed error information
- Include your Python version and operating system

## 🔄 Updates

To update to the latest version:
```bash
git pull origin main
pip3 install -r requirements.txt
```

## 🌟 Star This Project

If you find this project helpful, please give it a star ⭐ on GitHub!

---

**Made with ❤️ for the Telegram community**
- Try getting the chat ID again

### "Permission Denied"
- You might not have permission to send messages in that group
- Check if the group has restrictions for new members
- Verify you're not muted in the group

### "Flood Wait Error"
- This is normal - the bot will wait automatically
- Consider increasing delays between messages
- Reduce the number of groups or daily limits

## Support

If you encounter issues:
1. Check the error messages - they usually explain the problem
2. Verify your group chat IDs are correct
3. Make sure you have permission to send messages in all groups
4. Try reducing the number of messages or increasing delays

Remember: Always use this tool responsibly and respect Telegram's terms of service!
