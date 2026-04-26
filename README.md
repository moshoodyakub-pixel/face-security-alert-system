# 🔐 Face Security Alert System

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![DeepFace](https://img.shields.io/badge/DeepFace-0.0.79-orange.svg)](https://github.com/serengil/deepface)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

**A 24/7 home security system using face recognition with real-time alerts via Telegram and desktop notifications.**

Built with Python, DeepFace, and Jupyter Lab as a learning and portfolio project for an intermediate Python developer (MIVA student). Features CPU-optimized face recognition, multi-channel alerts, and comprehensive documentation.

[Features](#-features) • [Quick Start](#-quick-start) • [Demo](#-demo) • [Documentation](#-documentation) • [Installation](#-installation)

---

## 🎯 Features

### Core Security Features
- ✅ **24/7 Monitoring**: Continuous face detection and recognition
- ✅ **Unknown Face Detection**: Instant alerts when unrecognized person appears
- ✅ **Multi-Channel Alerts**: Telegram messages + Desktop notifications
- ✅ **Photo Evidence**: Automatic capture and storage of unknown faces
- ✅ **Smart Cooldown**: Prevents alert spam with configurable cooldown periods
- ✅ **Detection Threshold**: Requires 3+ seconds of continuous detection to reduce false alarms

### Technical Features
- 🎥 **Live Video Feed**: Real-time display with bounding boxes and labels
- 🔍 **Multiple Recognition Models**: VGG-Face, Facenet, ArcFace, and more
- 📊 **Performance Optimized**: CPU-friendly with frame skipping and resolution adjustment
- 📝 **Comprehensive Logging**: Detailed logs with rotation and date-based files
- ⚙️ **Highly Configurable**: Easy-to-edit config file for all settings
- 🔧 **Modular Design**: Clean, reusable, well-documented code

### User Experience
- 📓 **Interactive Notebooks**: Step-by-step Jupyter tutorials
- 💻 **CLI Scripts**: Production-ready command-line tools
- 📱 **Telegram Integration**: Remote alerts with photo attachments
- 🖥️ **Desktop Notifications**: Local Windows toast notifications
- 📚 **Extensive Documentation**: Setup guides, troubleshooting, architecture notes

---

## 🚀 Quick Start

### Windows One-Click Setup (Recommended)

Four batch scripts are included so you never have to open a terminal after the initial setup:

| Script | Purpose |
|--------|---------|
| `setup.bat` | **Run once** – creates a virtual environment and installs all dependencies |
| `start.bat` | Starts the security system (double-click or use the desktop shortcut) |
| `stop.bat` | Stops a running instance from another window or the desktop shortcut |
| `create_shortcuts.bat` | Places **"Face Security – Start"** and **"Face Security – Stop"** shortcuts on your Desktop |

#### First-time setup (4 steps)

```
1. Clone / download this repository to your PC
2. Double-click  setup.bat          ← installs everything
3. Double-click  create_shortcuts.bat  ← adds shortcuts to your Desktop
4. Use the shortcuts or the scripts below to add faces, then start the system
```

```bat
REM Add your face photos and build the recognition database
python scripts\add_new_person.py
python scripts\train_known_faces.py
```

After that just double-click the **"Face Security – Start"** shortcut on your Desktop.  
Press **Q** in the video window (or double-click **"Face Security – Stop"**) to stop.

### Command-Line Setup (Alternative)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your face photos and build database
python scripts/add_new_person.py
python scripts/train_known_faces.py

# 3. Run the security system
python scripts/run_security_system.py
```

That's it! The system will start monitoring with your webcam. Press `q` to quit.

### For Telegram Alerts (Optional but Recommended)

1. Create a Telegram bot via [@BotFather](https://t.me/botfather)
2. Get your chat ID from [@userinfobot](https://t.me/userinfobot)
3. Add credentials to `.env` file:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

See [TELEGRAM_SETUP.md](docs/TELEGRAM_SETUP.md) for detailed guide.

---

## 📸 Demo

### Live Monitoring
```
╔═══════════════════════════════════════════════════╗
║  🔴 MONITORING ACTIVE                            ║
║  ┌─────────────────────────────────────────┐     ║
║  │                                         │     ║
║  │  ┌──────────────────────┐              │     ║
║  │  │ John Doe - 95.3%     │              │     ║
║  │  │ [Green Box]          │              │     ║
║  │  └──────────────────────┘              │     ║
║  │                                         │     ║
║  │       ┌─────────────────┐               │     ║
║  │       │ Unknown - 78.2% │               │     ║
║  │       │ [Red Box]       │               │     ║
║  │       └─────────────────┘               │     ║
║  │                                         │     ║
║  │  FPS: 3.2                               │     ║
║  │  2025-10-10 21:45:32                    │     ║
║  └─────────────────────────────────────────┘     ║
╚═══════════════════════════════════════════════════╝
```

### Telegram Alert
```
⚠️ SECURITY ALERT

Unknown person detected!

Time: 2025-10-10 21:45:32
Confidence: 78.2%

[Photo Attached]
```

---

## 🏗️ Project Structure

```
face-security-alert-system/
├── 📋 README.md                    # This file
├── 📦 requirements.txt             # Python dependencies
├── ⚙️ config.py                    # Configuration settings
├── 🔒 .env.example                 # Environment template
├── 🚫 .gitignore                   # Git ignore rules
├── 🪟 setup.bat                    # One-time setup (venv + dependencies)
├── ▶️  start.bat                    # Start the security system
├── ⏹️  stop.bat                     # Stop the security system
├── 🔗 create_shortcuts.bat         # Create Desktop shortcuts
│
├── 📓 notebooks/                   # Jupyter Lab tutorials
│   ├── 01_setup_and_testing.ipynb
│   ├── 02_build_face_database.ipynb
│   ├── 03_test_recognition.ipynb
│   └── 04_run_security_system.ipynb
│
├── 🐍 scripts/                     # Production scripts
│   ├── train_known_faces.py
│   ├── run_security_system.py
│   └── add_new_person.py
│
├── 📦 src/                         # Core modules
│   ├── __init__.py
│   ├── face_detector.py            # Face detection
│   ├── face_recognizer.py          # Face recognition
│   ├── database_manager.py         # Database management
│   ├── alert_system.py             # Alert handling
│   └── camera_handler.py           # Camera operations
│
├── 🔧 utils/                       # Utility modules
│   ├── __init__.py
│   ├── logger.py                   # Logging configuration
│   └── image_processing.py         # Image utilities
│
├── 💾 data/                        # Data storage
│   ├── known_faces/                # Known people photos
│   ├── unknown_faces/              # Unknown face captures
│   └── encodings/                  # Face database
│
├── 📝 logs/                        # System logs
│
└── 📚 docs/                        # Documentation
    ├── SETUP.md                    # Installation guide
    ├── USAGE.md                    # Usage guide
    ├── TELEGRAM_SETUP.md           # Telegram configuration
    ├── ARCHITECTURE.md             # System design
    ├── TROUBLESHOOTING.md          # Common issues
    └── FACE_RECOGNITION_NOTES.md   # Technical notes
```

---

## 🛠️ Technology Stack

### Core Technologies
| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.8+ | Main language |
| **DeepFace** | 0.0.79 | Face recognition library |
| **OpenCV** | 4.8.1 | Computer vision & camera |
| **TensorFlow** | 2.13.0 | Deep learning backend |
| **NumPy** | 1.24.3 | Numerical computing |

### Integration & Tools
| Technology | Purpose |
|------------|---------|
| **python-telegram-bot** | Telegram alerts |
| **Plyer** | Desktop notifications |
| **Jupyter Lab** | Interactive development |
| **python-dotenv** | Environment configuration |

### Recognition Models (Configurable)
- VGG-Face (default) - Balanced speed/accuracy
- Facenet - Fastest
- ArcFace - Most accurate
- DeepFace, OpenFace, Dlib - Additional options

---

## 📦 Installation

### Prerequisites
- Windows 10/11
- Python 3.8 or higher
- Webcam (built-in or USB)
- 4GB RAM minimum (8GB recommended)

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/moshoodyakub-pixel/face-security-alert-system.git
   cd face-security-alert-system
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment** (optional)
   ```bash
   copy .env.example .env
   # Edit .env with your Telegram credentials
   ```

5. **Verify installation**
   ```bash
   python -c "import cv2, tensorflow, deepface; print('✅ All packages installed!')"
   ```

For detailed installation instructions, see [SETUP.md](docs/SETUP.md).

---

## 📖 Documentation

### User Guides
- **[Setup Guide](docs/SETUP.md)** - Complete installation walkthrough
- **[Usage Guide](docs/USAGE.md)** - How to use all features
- **[Telegram Setup](docs/TELEGRAM_SETUP.md)** - Configure Telegram alerts
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

### Technical Documentation
- **[Architecture](docs/ARCHITECTURE.md)** - System design and components
- **[Face Recognition Notes](docs/FACE_RECOGNITION_NOTES.md)** - Technical deep dive

### Interactive Tutorials
- **[Notebook 1: Setup & Testing](notebooks/01_setup_and_testing.ipynb)** - Verify installation
- **[Notebook 2: Build Database](notebooks/02_build_face_database.ipynb)** - Add known faces
- **[Notebook 3: Test Recognition](notebooks/03_test_recognition.ipynb)** - Test accuracy
- **[Notebook 4: Run System](notebooks/04_run_security_system.ipynb)** - Full monitoring

---

## ⚙️ Configuration

Key settings in `config.py`:

```python
# Camera settings
CAMERA_CONFIG = {
    "source": 0,        # 0 = built-in, 1 = USB
    "width": 640,
    "height": 480,
    "fps": 30,
}

# Recognition settings
RECOGNITION_CONFIG = {
    "model": "VGG-Face",     # Recognition model
    "threshold": 0.4,        # Similarity threshold (0.3-0.5)
    "distance_metric": "cosine",
}

# Alert settings
ALERT_CONFIG = {
    "cooldown_seconds": 30,              # Min time between alerts
    "detection_threshold_seconds": 3,     # Continuous detection time
    "enable_telegram": True,
    "enable_desktop": True,
}
```

All settings are fully documented with comments in the file.

---

## 🎓 Learning Objectives

This project was built as a learning exercise covering:

### Python Skills
- ✅ Object-oriented programming
- ✅ Modular code design
- ✅ Error handling and logging
- ✅ File I/O and data persistence
- ✅ Configuration management

### Computer Vision
- ✅ Face detection techniques
- ✅ Face recognition pipelines
- ✅ Image preprocessing
- ✅ Real-time video processing

### Software Engineering
- ✅ Project structure and organization
- ✅ Documentation and README files
- ✅ Version control (Git)
- ✅ Configuration over code
- ✅ Testing and validation

### Integration
- ✅ API integration (Telegram)
- ✅ System notifications
- ✅ Environment variables
- ✅ Multi-platform compatibility

---

## 🚀 Future Enhancements

Planned features and improvements:

### Short Term
- [ ] Web interface for monitoring
- [ ] Multiple camera support
- [ ] Email notifications
- [ ] Mobile app (Android/iOS)

### Long Term
- [ ] GPU acceleration support
- [ ] Cloud storage integration
- [ ] Face mask detection
- [ ] Liveness detection (anti-spoofing)
- [ ] Docker containerization
- [ ] Home Assistant integration

### Research
- [ ] Advanced models (ArcFace optimization)
- [ ] Edge device deployment (Raspberry Pi)
- [ ] 3D face recognition
- [ ] Emotion detection

---

## 🤝 Contributing

Contributions are welcome! This is a learning project, so all levels of contributions are appreciated.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Areas for Contribution
- 🐛 Bug fixes
- 📝 Documentation improvements
- ✨ New features
- 🧪 Tests
- 🎨 UI/UX improvements
- 🌐 Translations

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### What This Means
- ✅ Free to use, modify, and distribute
- ✅ Can be used commercially
- ✅ No warranty provided
- ℹ️ Must include original copyright notice

---

## 👨‍💻 Author

**MIVA Student** - Intermediate Python Developer

This project was created as part of my learning journey in computer vision and machine learning. It demonstrates practical application of face recognition technology with real-world security use cases.

### Connect
- 📧 [Create an Issue](https://github.com/moshoodyakub-pixel/face-security-alert-system/issues) for questions or bugs
- ⭐ [Star this repo](https://github.com/moshoodyakub-pixel/face-security-alert-system) if you find it helpful!
- 🔗 GitHub: [@moshoodyakub-pixel](https://github.com/moshoodyakub-pixel)

---

## 🙏 Acknowledgments

### Technologies & Libraries
- **[DeepFace](https://github.com/serengil/deepface)** by Sefik Ilkin Serengil - High-level face recognition library
- **[OpenCV](https://opencv.org/)** - Computer vision library
- **[TensorFlow](https://www.tensorflow.org/)** - Deep learning framework
- **[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)** - Telegram Bot API wrapper

### Inspiration & Resources
- Face recognition research papers (VGG-Face, FaceNet, ArcFace)
- OpenCV tutorials and documentation
- DeepFace GitHub repository and examples
- Computer vision community on Stack Overflow

### Special Thanks
- MIVA program for the learning opportunity
- Open source community for amazing tools
- Everyone who contributes to this project

---

## 📊 Project Stats

- **Lines of Code**: ~5,000+ (Python)
- **Documentation**: 6 comprehensive guides
- **Jupyter Notebooks**: 4 interactive tutorials
- **Modules**: 10 reusable components
- **Test Coverage**: Manual testing (automated tests planned)

---

## ❓ FAQ

<details>
<summary><b>Can this run on Raspberry Pi?</b></summary>
Yes, but performance will be slower. Use lower resolution and higher frame skip values. Consider using lightweight models.
</details>

<details>
<summary><b>Does it work with multiple cameras?</b></summary>
Not currently, but it's planned for future versions. You can run multiple instances with different camera sources.
</details>

<details>
<summary><b>Can someone fool it with a photo?</b></summary>
Yes, currently it can be fooled by photos. Liveness detection is planned for future versions.
</details>

<details>
<summary><b>How many people can it recognize?</b></summary>
Tested with 1-5 people. Should work with 20+ but may slow down. Database size affects performance.
</details>

<details>
<summary><b>Does it work in the dark?</b></summary>
No, it requires good lighting for face detection. Consider adding IR camera for night vision.
</details>

---

## 🔗 Quick Links

- [📋 Issues](https://github.com/moshoodyakub-pixel/face-security-alert-system/issues) - Report bugs or request features
- [📚 Documentation](docs/) - Comprehensive guides
- [💻 Source Code](src/) - Well-documented code
- [📓 Notebooks](notebooks/) - Interactive tutorials
- [⚙️ Configuration](config.py) - All settings

---

## 📞 Support

Having issues? Here's how to get help:

1. **Check Documentation**: See [docs/](docs/) folder
2. **Common Issues**: Check [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
3. **Create Issue**: [GitHub Issues](https://github.com/moshoodyakub-pixel/face-security-alert-system/issues)
4. **Review Logs**: Check `logs/` directory for errors

---

<div align="center">

**If you found this project helpful, please consider giving it a ⭐️!**

Made with ❤️ and Python by a MIVA student

[Back to Top](#-face-security-alert-system)

</div>
