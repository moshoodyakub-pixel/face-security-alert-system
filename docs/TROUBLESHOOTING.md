# Troubleshooting Guide

Common issues and solutions for the Face Security Alert System.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Camera Issues](#camera-issues)
- [Recognition Issues](#recognition-issues)
- [Performance Issues](#performance-issues)
- [Alert Issues](#alert-issues)
- [System Errors](#system-errors)

---

## Installation Issues

### TensorFlow Installation Failed

**Symptoms**: Error during `pip install tensorflow`

**Solutions**:

1. **Try specific version**:
   ```bash
   pip install tensorflow==2.13.0 --no-cache-dir
   ```

2. **For older CPUs (no AVX support)**:
   ```bash
   pip install tensorflow==2.10.0
   ```

3. **Check Python version**:
   ```bash
   python --version
   # Must be 3.8-3.11 for TensorFlow 2.13
   ```

### OpenCV Won't Install

**Solutions**:

```bash
# Uninstall all OpenCV versions
pip uninstall opencv-python opencv-contrib-python opencv-python-headless

# Install fresh
pip install opencv-python==4.8.1.78
```

### DeepFace Import Error

**Symptoms**: `ModuleNotFoundError: No module named 'deepface'`

**Solutions**:

```bash
# Reinstall DeepFace
pip uninstall deepface
pip install deepface==0.0.79

# Verify installation
python -c "from deepface import DeepFace; print('OK')"
```

### Virtual Environment Issues

**Symptoms**: Packages installed but not found

**Solutions**:

```bash
# Deactivate current environment
deactivate

# Delete and recreate
rmdir /s venv
python -m venv venv
venv\Scripts\activate

# Reinstall everything
pip install -r requirements.txt
```

---

## Camera Issues

### Camera Not Detected

**Symptoms**: "Failed to open camera" error

**Solutions**:

1. **Check camera index**:
   ```python
   import cv2
   # Try different indices
   for i in range(5):
       cap = cv2.VideoCapture(i)
       if cap.isOpened():
           print(f"Camera found at index {i}")
           cap.release()
   ```

2. **Update config.py**:
   ```python
   CAMERA_CONFIG = {
       "source": 1,  # Try 1 for external USB camera
   }
   ```

3. **Check Windows privacy settings**:
   - Settings → Privacy → Camera
   - Enable camera access for apps

4. **Close other applications**:
   - Skype, Teams, Zoom, etc.
   - Only one app can use camera at a time

### Camera Permissions Denied

**Windows Solutions**:

1. **Enable camera in Settings**:
   - Settings → Privacy → Camera
   - Turn on "Allow apps to access your camera"
   - Turn on "Allow desktop apps to access your camera"

2. **Check antivirus/firewall**:
   - May block camera access
   - Add Python to exceptions

### Poor Video Quality

**Solutions**:

1. **Increase resolution**:
   ```python
   CAMERA_CONFIG = {
       "width": 1280,
       "height": 720,
   }
   ```

2. **Clean camera lens**

3. **Improve lighting**

4. **Adjust camera focus** (if manual)

---

## Recognition Issues

### Low Recognition Accuracy

**Symptoms**: System doesn't recognize known faces

**Solutions**:

1. **Add more photos** (5-7 recommended):
   ```bash
   python scripts/add_new_person.py
   ```

2. **Increase threshold** (more lenient):
   ```python
   RECOGNITION_CONFIG = {
       "threshold": 0.5,  # Higher = more lenient
   }
   ```

3. **Use better quality photos**:
   - Good lighting
   - Clear focus
   - Face directly at camera
   - Multiple angles

4. **Rebuild database**:
   ```bash
   python scripts/train_known_faces.py
   ```

### Too Many False Alarms

**Symptoms**: Unknown alerts for known people

**Solutions**:

1. **Increase detection threshold**:
   ```python
   ALERT_CONFIG = {
       "detection_threshold_seconds": 5,  # Require 5s detection
   }
   ```

2. **Update photos**:
   - Especially if appearance changed
   - Glasses, beard, hairstyle, etc.

3. **Adjust recognition threshold**:
   ```python
   RECOGNITION_CONFIG = {
       "threshold": 0.45,  # Slightly more lenient
   }
   ```

### Wrong Person Identified

**Symptoms**: System confuses people

**Solutions**:

1. **Lower threshold** (stricter):
   ```python
   RECOGNITION_CONFIG = {
       "threshold": 0.35,  # Lower = stricter
   }
   ```

2. **Check for similar faces in database**:
   - Review all photos
   - Remove duplicates
   - Ensure clear differences

3. **Try different model**:
   ```python
   RECOGNITION_CONFIG = {
       "model": "Facenet",  # Alternative model
       "threshold": 0.4,
   }
   ```

### System Never Detects Faces

**Symptoms**: No faces detected at all

**Solutions**:

1. **Test face detection**:
   ```python
   from deepface import DeepFace
   import cv2
   
   cap = cv2.VideoCapture(0)
   ret, frame = cap.read()
   cap.release()
   
   faces = DeepFace.extract_faces(
       img_path=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
       detector_backend='opencv',
       enforce_detection=False
   )
   print(f"Detected {len(faces)} faces")
   ```

2. **Check lighting**:
   - Too dark or too bright affects detection
   - Use good ambient lighting

3. **Check distance from camera**:
   - Face should fill 20-40% of frame
   - Not too close or far

4. **Try different backend**:
   ```python
   DETECTION_CONFIG = {
       "backend": "ssd",  # or "mtcnn", "retinaface"
   }
   ```

---

## Performance Issues

### System is Slow/Laggy

**Solutions**:

1. **Increase frame skipping**:
   ```python
   DETECTION_CONFIG = {
       "process_every_n_frames": 3,  # Process every 3rd frame
   }
   ```

2. **Reduce resolution**:
   ```python
   CAMERA_CONFIG = {
       "width": 480,
       "height": 360,
   }
   ```

3. **Use faster backend**:
   ```python
   DETECTION_CONFIG = {
       "backend": "opencv",  # Fastest
   }
   ```

4. **Close unnecessary apps**:
   - Free up CPU and RAM

5. **Disable video display**:
   ```python
   DISPLAY_CONFIG = {
       "show_video": False,  # Run headless
   }
   ```

### High CPU Usage

**Solutions**:

```python
# Reduce processing load
DETECTION_CONFIG = {
    "process_every_n_frames": 4,
}

CAMERA_CONFIG = {
    "width": 480,
    "height": 360,
    "fps": 20,
}

PERFORMANCE_CONFIG = {
    "enable_frame_skip": True,
}
```

### Memory Leak

**Symptoms**: Memory usage grows over time

**Solutions**:

1. **Already implemented**: Cleanup every 1000 frames

2. **Restart periodically**:
   ```batch
   @echo off
   :loop
   python scripts/run_security_system.py
   timeout /t 10
   goto loop
   ```

3. **Check logs**:
   - Look for memory warnings
   - Check `logs/` directory

---

## Alert Issues

### Telegram Alerts Not Working

**Solutions**:

1. **Verify credentials**:
   ```bash
   python -c "from config import TELEGRAM_CONFIG; print(TELEGRAM_CONFIG)"
   ```

2. **Test connection**:
   ```python
   from src.alert_system import AlertSystem
   from config import *
   
   alert_system = AlertSystem(
       telegram_bot_token=TELEGRAM_CONFIG['bot_token'],
       telegram_chat_id=TELEGRAM_CONFIG['chat_id'],
       enable_telegram=True
   )
   
   alert_system.test_telegram_connection()
   ```

3. **Check .env file**:
   - No extra spaces
   - No quotes around values
   - Correct token format

4. **Verify bot is started**:
   - Send message to your bot in Telegram
   - Must start conversation first

### Desktop Notifications Not Showing

**Solutions**:

1. **Check Windows notification settings**:
   - Settings → System → Notifications
   - Enable notifications

2. **Test notification**:
   ```python
   from plyer import notification
   notification.notify(
       title='Test',
       message='Testing notifications',
       timeout=5
   )
   ```

3. **Enable in config**:
   ```python
   ALERT_CONFIG = {
       "enable_desktop": True,
   }
   ```

### No Photos Saved

**Symptoms**: Unknown faces detected but no photos

**Solutions**:

1. **Check directory exists**:
   ```bash
   # Should exist with .gitkeep file
   dir data\unknown_faces
   ```

2. **Enable in config**:
   ```python
   ALERT_CONFIG = {
       "save_unknown_faces": True,
   }
   ```

3. **Check disk space**:
   - Ensure enough free space

4. **Check permissions**:
   - Python needs write access to data/ folder

### Too Many Alerts (Spam)

**Solutions**:

```python
ALERT_CONFIG = {
    "cooldown_seconds": 60,  # Increase cooldown
    "detection_threshold_seconds": 5,  # Require longer detection
    "max_alerts_per_hour": 10,  # Limit total alerts
}
```

---

## System Errors

### "ModuleNotFoundError"

**Solution**: Install missing module
```bash
pip install <module_name>
```

### "FileNotFoundError: data/encodings/face_encodings.pkl"

**Solution**: Database not built yet
```bash
python scripts/train_known_faces.py
```

### "Configuration warnings: Telegram bot token not configured"

**Solution**: Configure Telegram in `.env`
See [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md)

### "ValueError: No face detected"

**Not an error if `enforce_detection=False`**

If problematic:
```python
DETECTION_CONFIG = {
    "enforce_detection": False,  # Continue even if no face
}
```

### System Crashes on Start

**Solutions**:

1. **Check logs**:
   ```bash
   type logs\face_security_*.log
   ```

2. **Test components individually**:
   ```bash
   # Test camera
   python -c "from src.camera_handler import CameraHandler; cam = CameraHandler(); cam.open()"
   
   # Test database
   python -c "from src.database_manager import DatabaseManager; from config import *; db = DatabaseManager(**DATABASE_CONFIG); db.load_database()"
   ```

3. **Verify all dependencies**:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

### "RuntimeError: Insufficient memory"

**Solutions**:

1. **Reduce resolution**
2. **Close other applications**
3. **Restart computer**
4. **Add more RAM** (hardware)

---

## Debug Mode

Enable detailed logging:

```python
# In config.py
LOGGING_CONFIG = {
    "log_level": "DEBUG",  # More detailed logs
}
```

Run with verbose output:

```bash
python scripts/run_security_system.py 2>&1 | tee output.log
```

---

## Getting More Help

### Check Logs

```bash
# View latest log
type logs\face_security_*.log

# Search for errors
findstr "ERROR" logs\face_security_*.log
```

### System Information

```bash
python -c "import sys, platform; print(f'Python: {sys.version}'); print(f'Platform: {platform.system()} {platform.release()}')"
```

### Package Versions

```bash
pip list | findstr "deepface opencv tensorflow"
```

### Community Resources

- **GitHub Issues**: Report bugs
- **Documentation**: Check other MD files
- **Stack Overflow**: Search for similar issues

---

## Emergency Recovery

If nothing works:

```bash
# 1. Backup your data
xcopy data data_backup /E /I

# 2. Delete virtual environment
rmdir /s venv

# 3. Reinstall everything
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 4. Restore data
xcopy data_backup data /E /I
```

---

**Still having issues?** Create an issue on GitHub with:
- Error message
- System info (Python version, OS)
- Steps to reproduce
- Log file contents
