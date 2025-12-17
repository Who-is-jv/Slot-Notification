# ICAI Course Slot Availability Monitor

A completely **FREE**, 24/7 cloud-based monitoring system using GitHub Actions that checks ICAI course slot availability and sends instant Telegram notifications when slots become available.

## 🎯 Features

- ✅ **Free & 24/7**: Runs automatically on GitHub Actions (free tier)
- ✅ **Real-time Alerts**: Instant Telegram notifications when slots open
- ✅ **Multi-Course Monitoring**: Monitors 3 courses simultaneously
- ✅ **Automated**: No manual intervention required
- ✅ **Error Handling**: Graceful error handling and retries

## 📋 Monitored Courses

- Advanced (ICITSS) MCS Course
- ICITSS - Information Technology
- ICITSS - Orientation Course

**Region**: Southern  
**POU**: HYDERABAD

## 🚀 Quick Setup Guide

### Step 1: Fork This Repository

1. Click the "Fork" button at the top right of this repository
2. This creates your own copy where you can set up the monitoring

### Step 2: Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. **Save the BOT_TOKEN** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 3: Get Your Telegram Chat ID

1. Search for **@userinfobot** on Telegram
2. Start a conversation with it
3. It will reply with your Chat ID (a number like: `123456789`)
4. **Save this CHAT_ID**

### Step 4: Configure GitHub Secrets

1. Go to your forked repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these two secrets:

   **Secret 1:**
   - Name: `TELEGRAM_BOT_TOKEN`
   - Value: Your bot token from Step 2

   **Secret 2:**
   - Name: `TELEGRAM_CHAT_ID`
   - Value: Your chat ID from Step 3

### Step 5: Enable GitHub Actions

1. Go to **Actions** tab in your repository
2. If prompted, click **"I understand my workflows, go ahead and enable them"**
3. The workflow will start running automatically!

## 📁 Project Structure

```
.
├── icai_slot_alert.py          # Main monitoring script
├── requirements.txt            # Python dependencies
├── .github/
│   └── workflows/
│       └── icai-monitor.yml    # GitHub Actions workflow
└── README.md                   # This file
```

## ⚙️ How It Works

1. **GitHub Actions** runs the script every 1 minute (cron schedule)
2. **Selenium** opens the ICAI website in headless Chrome
3. Script automatically:
   - Selects "Southern" region
   - Selects "HYDERABAD" POU
   - Checks each course for availability
   - Clicks "Get List" button
4. If slots are found, **Telegram notification** is sent immediately
5. Process repeats every minute

## 🔔 Notification Format

When a slot becomes available, you'll receive:

```
🚨 ICAI SLOT OPEN!

Course: <course name>
POU: Hyderabad

Book NOW!
```

## 🛠️ Customization

### Change Monitoring Frequency

Edit `.github/workflows/icai-monitor.yml`:

```yaml
schedule:
  - cron: '*/1 * * * *'  # Change */1 to */5 for every 5 minutes
```

Cron format: `minute hour day month day-of-week`

### Monitor Different Courses

Edit `icai_slot_alert.py`:

```python
COURSES_TO_MONITOR = [
    "Your Course Name Here",
    "Another Course Name"
]
```

### Change Region/POU

Edit `icai_slot_alert.py`:

```python
REGION = "Your Region"
POU = "YOUR POU"
```

## 📊 Monitoring Workflow Status

- Go to **Actions** tab in your repository
- You'll see the workflow runs with status:
  - ✅ Green checkmark = Success (no slots found or notification sent)
  - ❌ Red X = Error (check logs)

## 🐛 Troubleshooting

### Notifications Not Working?

1. **Check GitHub Secrets**: Ensure `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set correctly
2. **Test Bot**: Send a message to your bot manually in Telegram
3. **Check Chat ID**: Make sure you're using the correct Chat ID (not username)

### Script Errors?

1. Go to **Actions** tab → Click on failed run → Check logs
2. Common issues:
   - Website structure changed (may need script update)
   - Network timeout (will retry on next run)
   - Chrome driver issues (usually auto-resolved)

### Workflow Not Running?

1. Check if Actions are enabled: **Settings** → **Actions** → **General**
2. Ensure workflow file is in `.github/workflows/` directory
3. Check cron syntax is correct

## 🔒 Security Notes

- ✅ All sensitive data (bot token, chat ID) stored in GitHub Secrets
- ✅ No credentials hardcoded in the code
- ✅ Free GitHub Actions tier (no credit card required)
- ✅ Runs in isolated GitHub Actions environment

## 📝 GitHub Actions Free Tier Limits

- **2,000 minutes/month** for private repos
- **Unlimited minutes** for public repos (this project is public)
- Each run takes ~30-60 seconds
- Running every minute = ~43,200 minutes/month (well within limits for public repos)

## 🤝 Contributing

Feel free to:
- Report issues
- Suggest improvements
- Submit pull requests

## ⚠️ Disclaimer

- This tool is for **educational and personal use only**
- Use responsibly and in accordance with ICAI website terms of service
- The authors are not responsible for any misuse
- Always verify slot availability on the official website before booking

## 📄 License

Free to use and modify for personal purposes.

---

**Made with ❤️ for ICAI students**

*Last updated: 2024*


