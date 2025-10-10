# Setup Guide - Face Security Alert System

Complete installation guide for Windows 10/11 systems.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Steps](#installation-steps)
- [Verification](#verification)
- [Common Issues](#common-issues)
- [Next Steps](#next-steps)

---

## Prerequisites

### System Requirements

- **Operating System**: Windows 10 or Windows 11
- **Python**: Version 3.8 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: At least 2GB free space
- **Webcam**: Built-in or USB webcam
- **Internet**: Required for initial setup

### Required Software

1. **Python 3.8+**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
   
2. **Jupyter Lab** (for interactive development)
   - Will be installed via pip

3. **Git** (optional, for version control)
   - Download from: https://git-scm.com/download/win

---

## Installation Steps

### Step 1: Install Python

1. Download Python 3.8 or higher from python.org
2. Run the installer
3. **Important**: Check "Add Python 3.x to PATH"
4. Click "Install Now"
5. Verify installation:
   ```bash
   python --version
   ```
   Should show: `Python 3.8.x` or higher

### Step 2: Clone or Download Project

**Option A: Using Git**
```bash
git clone https://github.com/moshoodyakub-pixel/face-security-alert-system.git
cd face-security-alert-system
```

**Option B: Download ZIP**
1. Download ZIP from GitHub
2. Extract to desired location
3. Open Command Prompt or PowerShell in that directory

### Step 3: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows Command Prompt:
venv\Scripts\activate

# On Windows PowerShell:
venv\Scripts\Activate.ps1

# You should see (venv) in your prompt
```

**Note**: If PowerShell gives execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 4: Install Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

This will install:
- DeepFace (face recognition)
- OpenCV (computer vision)
- TensorFlow (deep learning backend)
- NumPy, Pillow (image processing)
- python-telegram-bot (alerts)
- plyer (desktop notifications)
- And more...

**Expected time**: 5-10 minutes depending on your internet speed

### Step 5: Install Jupyter Lab (For Interactive Development)

```bash
pip install jupyter jupyterlab
```

### Step 6: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` file with your text editor:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```

3. For now, you can leave these as placeholders. See [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) for getting credentials.

### Step 7: Verify Installation

Run the verification script:

```bash
python -c "import cv2, tensorflow, deepface; print('✅ All core packages installed!')"
```

Or run the test notebook:
```bash
jupyter lab notebooks/01_setup_and_testing.ipynb
```

---

## Verification

### Test Webcam Access

```bash
python -c "import cv2; cap = cv2.VideoCapture(0); print('✅ Webcam working!' if cap.isOpened() else '❌ Webcam not accessible'); cap.release()"
```

### Test Face Detection

Create a test file `test_detection.py`:
```python
import cv2
from deepface import DeepFace

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
cap.release()

if ret:
    faces = DeepFace.extract_faces(
        img_path=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
        detector_backend='opencv',
        enforce_detection=False
    )
    print(f"✅ Detected {len(faces)} face(s)")
else:
    print("❌ Could not capture frame")
```

Run it:
```bash
python test_detection.py
```

---

## Common Issues

### Issue 1: "Python is not recognized"

**Solution**: Python not added to PATH
1. Reinstall Python
2. Check "Add Python to PATH" during installation
3. Or manually add to PATH:
   - System Properties → Environment Variables
   - Add Python installation directory to PATH

### Issue 2: TensorFlow Installation Fails

**Solution**: Try specific version
```bash
pip install tensorflow==2.13.0 --no-cache-dir
```

### Issue 3: OpenCV Not Working

**Solution**: Install additional packages
```bash
pip uninstall opencv-python
pip install opencv-python==4.8.1.78
```

### Issue 4: "Permission Denied" for Webcam

**Solution**: Check Windows privacy settings
1. Settings → Privacy → Camera
2. Enable "Allow apps to access your camera"
3. Restart the application

### Issue 5: Jupyter Lab Won't Start

**Solution**: Check if port is in use
```bash
jupyter lab --port=8889
```

### Issue 6: Import Errors

**Solution**: Verify virtual environment is activated
```bash
# Deactivate and reactivate
deactivate
venv\Scripts\activate

# Reinstall packages
pip install -r requirements.txt
```

### Issue 7: Slow Performance

**Solutions**:
1. Close other applications
2. Increase frame skip in `config.py`:
   ```python
   DETECTION_CONFIG = {
       "process_every_n_frames": 3,  # Process every 3rd frame
   }
   ```
3. Reduce resolution in `config.py`:
   ```python
   CAMERA_CONFIG = {
       "width": 480,
       "height": 360,
   }
   ```

---

## Configuration

### Camera Settings

Edit `config.py`:

```python
CAMERA_CONFIG = {
    "source": 0,  # 0 = built-in webcam, 1 = external USB camera
    "width": 640,
    "height": 480,
    "fps": 30,
}
```

### Recognition Sensitivity

Edit `config.py`:

```python
RECOGNITION_CONFIG = {
    "threshold": 0.4,  # Lower = stricter (0.3-0.5 recommended)
}
```

### Alert Settings

Edit `config.py`:

```python
ALERT_CONFIG = {
    "cooldown_seconds": 30,  # Time between alerts
    "detection_threshold_seconds": 3,  # Continuous detection time
    "enable_telegram": True,
    "enable_desktop": True,
}
```

---

## Next Steps

1. **Configure Telegram** (optional but recommended)
   - See [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md)

2. **Build Face Database**
   - Open `notebooks/02_build_face_database.ipynb`
   - Or see [USAGE.md](USAGE.md)

3. **Test Recognition**
   - Open `notebooks/03_test_recognition.ipynb`

4. **Run Security System**
   - Open `notebooks/04_run_security_system.ipynb`
   - Or run: `python scripts/run_security_system.py`

---

## Uninstallation

If you want to remove the system:

```bash
# Deactivate virtual environment
deactivate

# Delete project directory
# (Manually delete the folder)

# Or if using pip globally, uninstall packages
pip uninstall -r requirements.txt -y
```

---

## Getting Help

- **Issues**: Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Usage**: See [USAGE.md](USAGE.md)
- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **GitHub Issues**: Report bugs on the repository

---

**Installation complete? →** Continue to [USAGE.md](USAGE.md)
