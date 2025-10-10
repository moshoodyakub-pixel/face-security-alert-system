# Usage Guide - Face Security Alert System

Complete guide for using the Face Security Alert System.

## Table of Contents

- [Quick Start](#quick-start)
- [Building Face Database](#building-face-database)
- [Running the System](#running-the-system)
- [Managing Known Faces](#managing-known-faces)
- [Monitoring and Alerts](#monitoring-and-alerts)
- [Tips and Best Practices](#tips-and-best-practices)

---

## Quick Start

### 3-Step Quick Start

```bash
# 1. Add your photos to database
python scripts/add_new_person.py

# 2. Build the face database
python scripts/train_known_faces.py

# 3. Run security monitoring
python scripts/run_security_system.py
```

---

## Building Face Database

The face database stores images of people you want the system to recognize.

### Method 1: Using Jupyter Notebook (Recommended for Beginners)

1. Start Jupyter Lab:
   ```bash
   jupyter lab
   ```

2. Open `notebooks/02_build_face_database.ipynb`

3. Follow the interactive steps to:
   - Add photos
   - Build database
   - Verify contents

### Method 2: Using Command Line Script

```bash
python scripts/add_new_person.py
```

**Interactive prompts will guide you through**:
1. Enter person's name
2. Choose photo source (webcam or directory)
3. Capture/load photos (minimum 3)
4. Confirm and save

### Method 3: Manual File Organization

1. Create a directory structure:
   ```
   data/known_faces/
   ├── john_doe/
   │   ├── photo1.jpg
   │   ├── photo2.jpg
   │   └── photo3.jpg
   ├── jane_smith/
   │   ├── photo1.jpg
   │   ├── photo2.jpg
   │   └── photo3.jpg
   ```

2. Build the database:
   ```bash
   python scripts/train_known_faces.py
   ```

### Photo Requirements

**Quality Guidelines**:
- ✅ Clear, well-lit face
- ✅ Face looking at camera
- ✅ Minimal obstructions
- ✅ Various angles (front, slight left, slight right)
- ✅ Different lighting conditions
- ❌ Avoid blurry photos
- ❌ Avoid extreme angles
- ❌ Avoid heavy shadows

**Technical Requirements**:
- **Format**: JPG, JPEG, or PNG
- **Minimum**: 3 photos per person
- **Recommended**: 5-7 photos per person
- **Maximum**: 10 photos per person (system limit)

### Database Management

**List people in database**:
```python
from src.database_manager import DatabaseManager
from config import DATABASE_CONFIG

db_manager = DatabaseManager(**DATABASE_CONFIG)
people = db_manager.list_people()
print(people)
```

**Get database statistics**:
```python
stats = db_manager.get_database_stats()
print(f"Total people: {stats['num_people']}")
print(f"Total images: {stats['total_images']}")
```

---

## Running the System

### Using Jupyter Notebook

Best for learning and testing:

```bash
jupyter lab
# Open notebooks/04_run_security_system.ipynb
```

**Features**:
- Interactive monitoring
- Easy to stop/start
- Good for testing
- See real-time feedback

### Using Command Line Script

Best for 24/7 monitoring:

```bash
python scripts/run_security_system.py
```

**Controls**:
- Press `q` to quit
- Press `s` to take screenshot
- Press `Ctrl+C` for emergency stop

**Features**:
- Runs continuously
- Full logging
- Optimized performance
- Background-friendly

### Configuration

Before running, review `config.py`:

```python
# Camera settings
CAMERA_CONFIG = {
    "source": 0,  # 0 for built-in, 1 for USB
    "width": 640,
    "height": 480,
}

# Detection settings
DETECTION_CONFIG = {
    "backend": "opencv",  # Fast for CPU
    "process_every_n_frames": 2,  # Process every 2nd frame
}

# Recognition settings
RECOGNITION_CONFIG = {
    "model": "VGG-Face",  # Balanced model
    "threshold": 0.4,  # Moderate sensitivity
}

# Alert settings
ALERT_CONFIG = {
    "cooldown_seconds": 30,  # Min time between alerts
    "detection_threshold_seconds": 3,  # Continuous detection time
}
```

---

## Managing Known Faces

### Add New Person

```bash
python scripts/add_new_person.py
```

Follow the prompts to:
1. Enter name
2. Capture photos (or load from directory)
3. Rebuild database

### Update Existing Person

```bash
python scripts/add_new_person.py
# When prompted for name, enter existing person's name
# Choose "yes" to update
```

### Delete Person

Currently via Python:

```python
from src.database_manager import DatabaseManager
from config import DATABASE_CONFIG

db_manager = DatabaseManager(**DATABASE_CONFIG)
db_manager.delete_person("person_name")
```

Or manually:
1. Delete person's directory from `data/known_faces/`
2. Rebuild database: `python scripts/train_known_faces.py`

### Rebuild Database

After any changes to photos:

```bash
python scripts/train_known_faces.py
```

This will:
- Scan `data/known_faces/` directory
- Process all images
- Create new database file
- Validate contents

---

## Monitoring and Alerts

### Alert Types

**1. Telegram Alerts**
- Remote notifications
- With photo attachments
- Instant delivery
- See [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md)

**2. Desktop Notifications**
- Local Windows notifications
- Quick alerts
- No internet required
- Appear in system tray

**3. Saved Photos**
- Unknown faces automatically saved
- Location: `data/unknown_faces/`
- Timestamped filenames
- Review later

### Viewing Alerts

**Check saved unknown faces**:
```bash
# Windows Explorer
explorer data\unknown_faces

# Or via Python
from src.alert_system import AlertSystem
from config import ALERT_CONFIG

alert_system = AlertSystem(**ALERT_CONFIG)
stats = alert_system.get_alert_stats()
print(f"Total alerts: {stats['total_photos']}")
```

**Review logs**:
```bash
# View today's log
type logs\face_security_YYYYMMDD.log

# Or open in text editor
notepad logs\face_security_YYYYMMDD.log
```

### Alert Configuration

Edit `config.py` to customize:

```python
ALERT_CONFIG = {
    # Alert cooldown (prevents spam)
    "cooldown_seconds": 30,  # 30 seconds between alerts
    
    # Detection threshold (reduces false alarms)
    "detection_threshold_seconds": 3,  # Must see face for 3 seconds
    
    # Enable/disable alert channels
    "enable_telegram": True,
    "enable_desktop": True,
    
    # Save unknown face photos
    "save_unknown_faces": True,
    
    # Maximum alerts per hour (safety limit)
    "max_alerts_per_hour": 20,
}
```

---

## Tips and Best Practices

### For Best Recognition Accuracy

1. **Use quality photos**
   - Good lighting
   - Clear focus
   - Full face visible

2. **Multiple angles**
   - Front view
   - Slight left/right
   - Different expressions

3. **Update regularly**
   - Add new photos periodically
   - Update if appearance changes (glasses, beard, etc.)

4. **Test before deploying**
   - Use `notebooks/03_test_recognition.ipynb`
   - Verify all known faces are recognized
   - Check false positive rate

### For Optimal Performance

1. **Adjust frame processing**
   ```python
   DETECTION_CONFIG = {
       "process_every_n_frames": 3,  # Higher = faster, less accurate
   }
   ```

2. **Lower resolution if needed**
   ```python
   CAMERA_CONFIG = {
       "width": 480,
       "height": 360,
   }
   ```

3. **Close unnecessary applications**
   - Free up CPU
   - Especially video/graphics apps

4. **Use wired connection for Telegram**
   - More reliable than WiFi
   - Faster alert delivery

### For Security

1. **Keep `.env` file secure**
   - Never share bot tokens
   - Add to `.gitignore` (already done)

2. **Review unknown faces regularly**
   - Check `data/unknown_faces/`
   - Identify false alarms
   - Add to database if needed

3. **Monitor system logs**
   - Check for errors
   - Review alert frequency
   - Adjust thresholds as needed

4. **Test alert system**
   ```bash
   python -c "from src.alert_system import AlertSystem; from config import *; alert_system = AlertSystem(**TELEGRAM_CONFIG, **ALERT_CONFIG); alert_system.test_telegram_connection()"
   ```

### For 24/7 Operation

1. **Disable sleep mode**
   - Windows Settings → Power & Sleep
   - Set both to "Never"

2. **Auto-restart on crash** (optional)
   - Create batch file:
     ```batch
     @echo off
     :start
     python scripts/run_security_system.py
     timeout /t 10
     goto start
     ```

3. **Monitor disk space**
   - Unknown faces accumulate
   - Clean up periodically
   - Or set up log rotation

4. **Run as Windows service** (advanced)
   - Use NSSM (Non-Sucking Service Manager)
   - See online guides for setup

---

## Troubleshooting

### Recognition Not Working

1. **Check database**:
   ```bash
   python scripts/train_known_faces.py
   ```

2. **Adjust threshold**:
   ```python
   # In config.py
   RECOGNITION_CONFIG = {
       "threshold": 0.5,  # Try higher for more lenient
   }
   ```

3. **Add more photos**:
   - Need diverse angles/lighting
   - Minimum 3, recommended 5-7

### Too Many False Alarms

1. **Increase detection threshold**:
   ```python
   ALERT_CONFIG = {
       "detection_threshold_seconds": 5,  # Require 5 seconds
   }
   ```

2. **Increase alert cooldown**:
   ```python
   ALERT_CONFIG = {
       "cooldown_seconds": 60,  # 1 minute between alerts
   }
   ```

### Performance Issues

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions.

---

## Advanced Usage

### Custom Alert Logic

Create custom alert handler:

```python
from src.alert_system import AlertSystem

class CustomAlertSystem(AlertSystem):
    def send_alert(self, face_image, full_frame=None, confidence=0.0, additional_info=""):
        # Add your custom logic here
        # Example: Send email, trigger siren, etc.
        super().send_alert(face_image, full_frame, confidence, additional_info)
```

### Integration with Home Automation

Example with Home Assistant:

```python
import requests

def notify_home_assistant(event_type, data):
    url = "http://homeassistant.local:8123/api/events/face_detected"
    headers = {"Authorization": "Bearer YOUR_TOKEN"}
    requests.post(url, json=data, headers=headers)
```

### Remote Access

Use ngrok for remote access to video feed:

```bash
# Install ngrok
# Start system
python scripts/run_security_system.py

# In another terminal
ngrok http 8888
```

---

## Getting Help

- **Issues**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Setup**: [SETUP.md](SETUP.md)
- **Telegram**: [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

---

**Next:** Learn about [Telegram Setup](TELEGRAM_SETUP.md) for remote alerts
