# System Architecture

Technical overview of the Face Security Alert System design and implementation.

## Table of Contents

- [Overview](#overview)
- [System Components](#system-components)
- [Data Flow](#data-flow)
- [Face Recognition Pipeline](#face-recognition-pipeline)
- [Technology Stack](#technology-stack)
- [Performance Optimizations](#performance-optimizations)
- [Design Decisions](#design-decisions)

---

## Overview

The Face Security Alert System is a modular, CPU-optimized application designed for 24/7 home security monitoring using face recognition technology.

### Key Features

- Real-time face detection and recognition
- Multi-channel alerting (Telegram + Desktop)
- Alert cooldown and detection threshold
- Automatic unknown face capture
- Comprehensive logging
- Configurable and extensible

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   Face Security System                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌─────────────────┐                │
│  │ Camera       │──────▶│ Face Detector   │                │
│  │ Handler      │      │ (DeepFace)      │                │
│  └──────────────┘      └────────┬────────┘                │
│                                  │                          │
│                                  ▼                          │
│                       ┌──────────────────┐                 │
│                       │ Face Recognizer  │                 │
│                       │ (VGG-Face Model) │                 │
│                       └────────┬─────────┘                 │
│                                │                            │
│                    ┌───────────┴──────────┐                │
│                    │                      │                │
│                    ▼                      ▼                │
│         ┌─────────────────┐   ┌─────────────────┐         │
│         │ Known Face?     │   │ Unknown Face?   │         │
│         │ (Green Box)     │   │ (Red Box)       │         │
│         └─────────────────┘   └────────┬────────┘         │
│                                        │                   │
│                                        ▼                   │
│                             ┌─────────────────┐            │
│                             │ Alert System    │            │
│                             ├─────────────────┤            │
│                             │ - Telegram      │            │
│                             │ - Desktop       │            │
│                             │ - Save Photo    │            │
│                             └─────────────────┘            │
│                                                             │
│  ┌──────────────┐      ┌─────────────────┐                │
│  │ Database     │      │ Logger          │                │
│  │ Manager      │      │ Utility         │                │
│  └──────────────┘      └─────────────────┘                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## System Components

### 1. Camera Handler (`src/camera_handler.py`)

**Responsibilities**:
- Initialize and manage webcam
- Capture frames at specified resolution
- Display video feed with overlays
- Draw bounding boxes and labels
- Calculate and display FPS

**Key Methods**:
- `open()` - Initialize camera
- `read_frame()` - Capture single frame
- `display_frame()` - Show video window
- `draw_fps()` - Add FPS overlay
- `draw_timestamp()` - Add timestamp overlay

### 2. Face Detector (`src/face_detector.py`)

**Responsibilities**:
- Detect faces in images
- Extract face regions
- Calculate bounding boxes
- Filter by minimum size

**Technology**: DeepFace with OpenCV backend

**Key Methods**:
- `detect_faces()` - Detect all faces in frame
- `get_face_coordinates()` - Get bounding box
- `extract_face_region()` - Crop face from image
- `draw_face_box()` - Draw detection box

### 3. Face Recognizer (`src/face_recognizer.py`)

**Responsibilities**:
- Compare faces against database
- Calculate similarity scores
- Manage alert cooldowns
- Track continuous detections

**Technology**: DeepFace with VGG-Face model

**Key Methods**:
- `recognize_face()` - Identify person
- `verify_face()` - Compare two faces
- `should_send_alert()` - Check cooldown
- `update_detection_tracking()` - Track detections

### 4. Database Manager (`src/database_manager.py`)

**Responsibilities**:
- Load/save face encodings
- Manage known faces
- Validate database
- Add/update/delete people

**Storage**: Pickle format (Python serialization)

**Key Methods**:
- `load_database()` - Load face data
- `save_database()` - Persist changes
- `build_database()` - Process images
- `add_person()` - Add new person
- `delete_person()` - Remove person

### 5. Alert System (`src/alert_system.py`)

**Responsibilities**:
- Send Telegram messages
- Show desktop notifications
- Save unknown face photos
- Log alert events

**Channels**: Telegram, Desktop (Windows), Photo Storage

**Key Methods**:
- `send_alert()` - Send via all channels
- `send_telegram_alert()` - Telegram-specific
- `send_desktop_notification()` - Local alerts
- `save_unknown_face_photo()` - Store evidence

### 6. Logger Utility (`utils/logger.py`)

**Responsibilities**:
- Configure logging
- Rotate log files
- Format log messages
- Separate console/file output

**Features**: Date-based logs, size rotation, level filtering

### 7. Image Processing (`utils/image_processing.py`)

**Responsibilities**:
- Resize images
- Normalize pixel values
- Check image quality
- Color space conversion

**Features**: Quality metrics, enhancement, alignment

---

## Data Flow

### 1. Initialization Flow

```
Start Application
    ↓
Load Configuration (config.py)
    ↓
Initialize Components
    ↓
Load Face Database
    ↓
Open Camera
    ↓
Ready for Monitoring
```

### 2. Processing Flow (Per Frame)

```
Capture Frame
    ↓
Frame Skip? (Every Nth frame)
    ↓ Yes
Detect Faces (DeepFace + OpenCV)
    ↓
For Each Face:
    ├─ Extract Face Region
    ├─ Recognize Face (Compare to DB)
    ├─ Known Face?
    │   ├─ Yes: Draw Green Box
    │   └─ No:  Draw Red Box
    │           ↓
    │       Track Detection Time
    │           ↓
    │       Threshold Met?
    │           ↓ Yes
    │       Check Cooldown
    │           ↓ Valid
    │       Send Alert
    │           ├─ Telegram
    │           ├─ Desktop
    │           └─ Save Photo
    └─
Add Overlays (FPS, Timestamp, Status)
    ↓
Display Frame
    ↓
Check Exit Key
    ↓
Continue Loop
```

### 3. Database Building Flow

```
Scan known_faces/ Directory
    ↓
For Each Person:
    ├─ Load Images (JPG/PNG)
    ├─ Validate (Min 3 images)
    └─ Add to Database
    ↓
Save Database (Pickle)
    ↓
Validate Contents
    ↓
Export Info File
```

---

## Face Recognition Pipeline

### 5-Stage Pipeline

1. **Face Detection**
   - Input: Raw image/frame
   - Process: Locate face regions
   - Output: Bounding boxes + confidence
   - Technology: OpenCV Haar Cascade (via DeepFace)

2. **Face Alignment**
   - Input: Detected face
   - Process: Normalize rotation/position
   - Output: Aligned face image
   - Technology: DeepFace auto-alignment

3. **Feature Extraction**
   - Input: Aligned face
   - Process: Extract facial features
   - Output: 128/512-D embedding vector
   - Technology: VGG-Face CNN

4. **Face Matching**
   - Input: Feature vector + database
   - Process: Calculate similarity scores
   - Output: Best match + distance
   - Metric: Cosine distance

5. **Decision Making**
   - Input: Match results + threshold
   - Process: Apply business logic
   - Output: Known/Unknown decision
   - Features: Cooldown, detection threshold

---

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.8+ | Main programming language |
| Face Recognition | DeepFace | 0.0.79 | High-level face recognition |
| Computer Vision | OpenCV | 4.8.1 | Image processing, camera |
| Deep Learning | TensorFlow | 2.13.0 | Neural network backend |
| Numerics | NumPy | 1.24.3 | Array operations |
| Images | Pillow | 10.0.1 | Image manipulation |

### Integration Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Alerts | python-telegram-bot | Remote notifications |
| Desktop | Plyer | Windows notifications |
| Config | python-dotenv | Environment variables |
| Data | Pickle | Database serialization |

### Development Tools

| Tool | Purpose |
|------|---------|
| Jupyter Lab | Interactive development |
| Git | Version control |
| pip | Package management |

---

## Performance Optimizations

### CPU Optimization

1. **Frame Skipping**
   - Process every Nth frame
   - Default: Every 2nd frame
   - Reduces CPU load by 50%

2. **Lightweight Detection Backend**
   - OpenCV Haar Cascade
   - Fast, CPU-friendly
   - Good enough for security

3. **Efficient Model**
   - VGG-Face: Balanced speed/accuracy
   - Alternatives: Facenet (faster), ArcFace (better)

4. **Resolution Reduction**
   - 640x480 default
   - Lower = faster processing
   - Trade-off with accuracy

### Memory Optimization

1. **Pickle Storage**
   - Efficient serialization
   - Fast load times
   - Compact file size

2. **Lazy Loading**
   - Load database once
   - Keep in memory
   - No repeated disk I/O

3. **Cleanup Routines**
   - Clear old tracking data
   - Prevent memory leaks
   - Every 1000 frames

### Network Optimization

1. **Async Telegram**
   - Non-blocking sends
   - Doesn't slow detection
   - Handles network issues

2. **Image Compression**
   - JPEG for photos
   - Quality 85%
   - Reduced upload time

---

## Design Decisions

### Why DeepFace?

**Pros**:
- ✅ High-level API (easy to use)
- ✅ Multiple model options
- ✅ CPU-compatible
- ✅ Well-maintained
- ✅ Good documentation

**Cons**:
- ❌ Slower than dlib
- ❌ Larger dependencies
- ❌ Model download on first run

**Alternatives Considered**:
- `face_recognition`: Simpler but less flexible
- `dlib`: Faster but harder to install on Windows
- Custom CNN: Too complex for this use case

### Why VGG-Face Model?

**Reasons**:
- Balanced accuracy vs. speed
- Works well on CPU
- Good for 1-5 people database
- Proven reliability

**Threshold Choice** (0.4):
- Lower = stricter (fewer false positives)
- Higher = lenient (fewer false negatives)
- 0.4 = good balance for home use

### Why Pickle for Database?

**Pros**:
- ✅ Native Python
- ✅ Fast serialization
- ✅ Handles NumPy arrays
- ✅ Simple to use

**Cons**:
- ❌ Not human-readable
- ❌ Not portable to other languages
- ❌ Security concerns (trusted data only)

**Alternatives Considered**:
- JSON: Can't handle NumPy arrays
- SQLite: Overkill for this use case
- HDF5: More complex setup

### Why Two-Stage Alert System?

**Design**: Cooldown + Detection Threshold

**Rationale**:
1. **Cooldown** (30s): Prevents spam
2. **Threshold** (3s): Reduces false alarms

**Example**:
- Person walks by: Detected for 1s → No alert
- Person at door: Detected for 5s → Alert sent
- Same person returns: Within 30s → No alert

This eliminates most false positives while catching real threats.

---

## Security Considerations

### Data Privacy

- Face data stored locally
- No cloud uploads (except Telegram)
- `.env` for sensitive credentials
- `.gitignore` prevents data leaks

### Authentication

- Telegram bot token (secret)
- Chat ID (public-ish)
- No user authentication needed

### Anti-Spoofing

**Current**: None (photos can fool system)

**Future Improvements**:
- Liveness detection
- 3D depth sensing
- Blinking detection
- Texture analysis

---

## Extensibility

### Adding New Alert Channel

```python
from src.alert_system import AlertSystem

class EmailAlertSystem(AlertSystem):
    def send_alert(self, ...):
        # Your email logic
        super().send_alert(...)  # Call parent
```

### Adding New Recognition Model

Edit `config.py`:
```python
RECOGNITION_CONFIG = {
    "model": "Facenet",  # Or OpenFace, ArcFace, etc.
    "threshold": 0.4,    # Adjust per model
}
```

### Custom Face Database Format

```python
from src.database_manager import DatabaseManager

class SQLDatabaseManager(DatabaseManager):
    def load_database(self):
        # Load from SQL
        pass
    
    def save_database(self, database):
        # Save to SQL
        pass
```

---

## Future Improvements

### Performance
- [ ] GPU acceleration (CUDA)
- [ ] Model quantization
- [ ] Multi-threading
- [ ] C++ extensions

### Features
- [ ] Multiple camera support
- [ ] Person tracking across frames
- [ ] Face mask detection
- [ ] Age/gender estimation
- [ ] Emotion recognition

### Deployment
- [ ] Docker container
- [ ] Windows service
- [ ] Web interface
- [ ] Mobile app
- [ ] Cloud integration

---

## Related Documentation

- [Setup Guide](SETUP.md)
- [Usage Guide](USAGE.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Face Recognition Notes](FACE_RECOGNITION_NOTES.md)

---

**For technical questions**, see the source code comments or open an issue on GitHub.
