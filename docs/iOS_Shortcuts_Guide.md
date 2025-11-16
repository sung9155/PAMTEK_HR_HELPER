# iOS Shortcuts Automation Guide

Complete guide for automating Pamtek HR attendance checking using iPhone Shortcuts app.

## Overview

This guide shows how to use iPhone's Shortcuts app to semi-automate the Pamtek attendance system with location-based and time-based triggers.

## Prerequisites

1. **Server Running**
   - Flask server must be running on your PC or Docker container
   - iPhone and server must be on the same network (or use ngrok for external access)

2. **Server IP Address**
   - Find your server's local IP (e.g., 192.168.1.100)
   - Or use ngrok/cloud server for external access

3. **API Endpoints**
   - Status check: `http://[SERVER_IP]:5000/api/status`
   - Summary: `http://[SERVER_IP]:5000/api/summary`

---

## Shortcut 1: Morning Check-In Reminder

### How It Works
- **Trigger**: Arriving at office location
- **Time**: 8:00 AM ~ 9:30 AM
- **Actions**:
  1. Check attendance status via API
  2. Show notification if not checked in
  3. Open HR app automatically

### Setup Instructions

#### Step 1: Create New Shortcut

1. Open **Shortcuts** app on iPhone
2. Tap **+** button to create new shortcut
3. Name it: **"Check-In Reminder"**

#### Step 2: Add Actions

Add the following actions in order:

**1) Get Contents of URL**
- URL: `http://[SERVER_IP]:5000/api/status`
- Example: `http://192.168.1.100:5000/api/status`
- Method: GET

**2) Get Dictionary Value**
- Get: `is_weekend`
- From: `Contents of URL`

**3) If** (Check if weekend)
- Condition: `Dictionary Value` equals `true`

**4) Show Notification (inside If - Weekend)**
- Title: `It's Weekend!`
- Body: `Enjoy your day off!`

**5) Otherwise**

**6) Get Dictionary Value (inside Otherwise)**
- Get: `need_action`
- From: `Contents of URL`

**7) If (inside Otherwise)**
- Condition: `Dictionary Value` equals `true`

**8) Show Notification (inside nested If)**
- Title: `Check In Needed!`
- Body: `Please check in at the HR app.`

**9) Wait (inside nested If)**
- Duration: 2 seconds

**10) Open App (inside nested If)**
- App: Select your HR app (Pamtek or browser)

**11) Otherwise (inside nested If)**

**12) Show Notification (inside nested Otherwise)**
- Title: `Already Checked In`
- Body: `You're all set for today!`

**13) End If (close nested If)**

**14) End If (close weekend check)**

#### Step 3: Create Automation

1. Tap **Automation** tab at bottom
2. Tap **+** (Create Personal Automation)
3. Select **Arrive**

**Location Settings:**
- **Location**: Add your office address
- **Radius**: 100m ~ 500m (adjust as needed)

**Time Filter (Optional):**
If you want it to run only during work hours:
- Add **If** action
- Condition: `Current Date` formatted as `HH:mm` is between `08:00` and `09:30`

**Choose Shortcut:**
- Select the **"Check-In Reminder"** shortcut you created

**Automation Options:**
- ✅ **Ask Before Running**: Turn OFF (for automatic execution)
- ✅ **Notify When Run**: Turn ON (to see results)

---

## Shortcut 2: Evening Check-Out Reminder

### How It Works
- **Trigger**: Every day at 6:00 PM
- **Actions**:
  1. Check if already checked out
  2. Show notification if not checked out
  3. Open HR app

### Setup Instructions

#### Step 1: Create New Shortcut

1. Name: **"Check-Out Reminder"**

#### Step 2: Add Actions

**1) Get Contents of URL**
- URL: `http://[SERVER_IP]:5000/api/status`
- Method: GET

**2) Get Dictionary Value**
- Get: `is_weekend`
- From: `Contents of URL`

**3) If** (Check if weekend)
- Condition: `Dictionary Value` equals `true`

**4) Show Notification (inside If - Weekend)**
- Title: `It's Weekend!`
- Body: `No need to check out. Enjoy!`

**5) Otherwise**

**6) Get Dictionary Value (inside Otherwise)**
- Get: `is_checked_out`
- From: `Contents of URL`

**7) If (inside Otherwise)**
- Condition: `Dictionary Value` equals `false`

**8) Show Notification (inside nested If)**
- Title: `Check Out Reminder`
- Body: `Don't forget to check out before leaving!`

**9) Wait (inside nested If)**
- Duration: 2 seconds

**10) Open App (inside nested If)**
- App: Your HR app

**11) Otherwise (inside nested If)**

**12) Show Notification (inside nested Otherwise)**
- Title: `Already Checked Out`
- Body: `Great job today!`

**13) End If (close nested If)**

**14) End If (close weekend check)**

#### Step 3: Create Time-Based Automation

1. Go to **Automation** tab
2. Tap **+** (Create Personal Automation)
3. Select **Time of Day**

**Time Settings:**
- Time: `6:00 PM` (18:00)
- Repeat: **Daily** or **Custom** (weekdays only)

**Choose Shortcut:**
- Select **"Check-Out Reminder"**

**Automation Options:**
- ✅ **Ask Before Running**: Turn OFF
- ✅ **Notify When Run**: Turn ON

---

## Shortcut 3: Manual Status Check (Optional)

Quick check for current attendance status.

### Setup Instructions

**1) Get Contents of URL**
- URL: `http://[SERVER_IP]:5000/api/summary`
- Method: GET

**2) Get Dictionary Value**
- Get: `summary`
- From: `Contents of URL`

**3) Show Alert**
- Title: `Attendance Status`
- Message: `Dictionary Value`

**Add to Home Screen:**
- Tap shortcut settings (•••)
- Select **Add to Home Screen**
- Customize icon and name

---

## Advanced: Real-time Status Response

The server now refreshes the page on every API call, so you always get real-time data:

**JSON Response Example (Weekday):**
```json
{
  "is_checked_in": false,
  "is_checked_out": false,
  "check_in_time": null,
  "check_out_time": null,
  "status": "not_checked_in",
  "need_action": true,
  "is_weekend": false,
  "error": null
}
```

**JSON Response Example (Weekend):**
```json
{
  "is_checked_in": false,
  "is_checked_out": false,
  "check_in_time": null,
  "check_out_time": null,
  "status": "weekend",
  "need_action": false,
  "is_weekend": true,
  "error": null
}
```

**Status Values:**
- `not_checked_in`: Not checked in yet
- `not_checked_out`: Checked in, but not checked out
- `completed`: Both check-in and check-out completed
- `weekend`: It's weekend (Saturday or Sunday)
- `error`: Error occurred

**Weekend Detection:**
The server automatically detects weekends (Saturday and Sunday) and returns `is_weekend: true` with `need_action: false`. This prevents unnecessary notifications on weekends.

---

## Troubleshooting

### Cannot Connect to Server

**Causes:**
- PC and iPhone on different networks
- Server not running
- Incorrect IP address
- Firewall blocking connection

**Solutions:**
1. Verify server is running: `docker-compose ps` or check terminal
2. Ensure iPhone and server are on same WiFi
3. Verify IP address:
   - Windows: `ipconfig`
   - Mac/Linux: `ifconfig`
   - Docker: Use host machine's IP
4. Test with Safari: `http://[SERVER_IP]:5000/health`

### Automation Not Running

**Location-Based:**
- iPhone Settings → Privacy & Security → Location Services → Shortcuts → **"Always"**
- Increase location radius to 500m
- Make sure "Precise Location" is enabled

**Time-Based:**
- iPhone Settings → Shortcuts → Advanced → Enable **"Allow Running Scripts"**
- Check if Do Not Disturb is blocking notifications

### App Won't Open Automatically

- Verify correct app name
- Some apps may be restricted by iOS security policies
- Try opening Safari with URL scheme instead

---

## Using Docker Server

If running the server in Docker:

**1. Start Docker Container**
```bash
cd /path/to/Pamtek_HR_Helper
docker-compose up -d
```

**2. Find Server IP**
```bash
# On host machine
ipconfig  # Windows
ifconfig  # Mac/Linux
```

**3. Use Host IP in Shortcuts**
```
http://192.168.1.100:5000/api/status
```

**Note:** Use the **host machine's IP**, not the container IP.

---

## External Access (Optional)

To use outside your home/office network:

### Method 1: ngrok (Quick & Easy)

1. Install ngrok: https://ngrok.com/
2. Run ngrok:
   ```bash
   ngrok http 5000
   ```
3. Use the generated URL in Shortcuts:
   ```
   https://xxxx-xxx-xxx-xxx.ngrok-free.app/api/status
   ```

**Pros:** Quick setup, HTTPS included
**Cons:** URL changes on restart (use paid version for static URL)

### Method 2: Cloud Deployment

Deploy to cloud services:
- **AWS EC2 / Lightsail**
- **Google Cloud Platform**
- **DigitalOcean**
- **Heroku**

Use static IP or domain name.

---

## Security Considerations

⚠️ **Important Security Notes:**

1. **Do not expose server URL publicly** without authentication
2. **Use HTTPS** when accessing externally (ngrok provides this)
3. **Add authentication** for production use:
   - API key header
   - Bearer token
   - Basic auth
4. **Firewall rules**: Only allow necessary ports
5. **Keep credentials secure**: Never commit `.env` to git

---

## Tips & Best Practices

1. **Battery Saving**: Location-based automations use more battery. Combine with time filters.
2. **Test First**: Run shortcuts manually before enabling automation.
3. **Notification Volume**: Make sure notification sounds are loud enough.
4. **Weekend Logic**: ✅ **Already Built-in!** The server automatically detects weekends and shows friendly messages like "It's Weekend!" instead of check-in reminders.
5. **Multiple Locations**: Create separate automations for different office locations.
6. **Vacation Days**: The weekend detection only covers Saturday/Sunday. For holidays, you might want to add custom date checks in Shortcuts.

---

## API Reference

### GET /api/status

Returns current attendance status with automatic weekend detection.

**Response (Weekday):**
```json
{
  "is_checked_in": true,
  "is_checked_out": false,
  "check_in_time": "08:45",
  "check_out_time": null,
  "status": "not_checked_out",
  "need_action": true,
  "is_weekend": false,
  "error": null
}
```

**Response (Weekend):**
```json
{
  "is_checked_in": false,
  "is_checked_out": false,
  "check_in_time": null,
  "check_out_time": null,
  "status": "weekend",
  "need_action": false,
  "is_weekend": true,
  "error": null
}
```

### GET /api/summary

Returns simple text summary.

**Response:**
```json
{
  "summary": "출근: 08:45 (퇴근 전)"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

---

## Example Shortcuts Gallery

### Quick Actions Widget

Add to iPhone home screen or widget for one-tap access:

1. **Check Status** - Shows current attendance state
2. **Open HR App** - Quick launch with deep link
3. **Send Status to Watch** - Push notification to Apple Watch

### Advanced Automation

**Geofence with Time Window:**
```
Arrive at Office
  AND Time is between 08:00-09:30
  AND Day is weekday
    → Check if not checked in
      → Show notification
      → Open app
```

**Smart Evening Reminder:**
```
Time is 18:00
  AND Location is at Office
  AND Not checked out
    → Show persistent notification
    → Open app
```

---

## Next Steps

After setup is complete:

1. ✅ Test both shortcuts manually
2. ✅ Enable automations
3. ✅ Wait for tomorrow morning to test location trigger
4. ✅ Adjust location radius and time windows as needed
5. ✅ Check server logs if issues occur
6. ✅ Add to Apple Watch for quick access

---

## Support

**Check Server Logs:**
```bash
# Docker
docker-compose logs -f

# Direct Python
Check terminal output
```

**Common Issues:**
- API returns error → Check server logs
- No notification → Check iOS notification settings
- App doesn't open → Verify app name in action

---

## Version Info

- Server: Selenium-based (real-time data)
- API Version: v1.0
- iOS Compatibility: iOS 14+
- Shortcuts App: iOS built-in

Last updated: 2024-11-15
