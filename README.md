# H.A.N.D.S: A Braille Navigation System

A computer vision-based assistive tool that helps visually impaired users locate braille signage by providing real-time audio guidance.
Made during HackHives 36 hour hackathon.

## Overview

This system acts as a "smart guide" for finding braille signs in public spaces. Using a webcam, it detects both braille text and the user's hand, then provides verbal directions to guide the user's finger directly to the braille.

**The Problem:** Braille signs are often small, placed at varying heights, and difficult to locate without extensive tactile searching.

**Our Solution:** Real-time computer vision that "sees" both the braille and your hand, offering audio feedback like "Move left" or "Move up" until your hand is centered on the target.

## Features

- **Hand Tracking**: Uses MediaPipe to detect and track the user's index finger in real-time
- **Braille Detection**: Deep learning model identifies braille signage in the camera frame
- **Audio Guidance**: Text-to-speech provides clear directional commands
- **Lock-on Mode**: Can lock onto a detected braille sign for stable tracking

## Tech Stack

- **Python 3.8+**
- **OpenCV**: Video capture and image processing
- **MediaPipe**: Hand landmark detection
- **YOLO**: Braille sign detection
- **pyttsx3**: Offline text-to-speech
- **NumPy**: Geometric calculations

## Demo

[![H.A.N.D.S demo](https://img.youtube.com/vi/AjK3c1EMH4o/0.jpg)](https://www.youtube.com/watch?v=AjK3c1EMH4o)
## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Connect a webcam to your computer
2. Run the main script:
   ```bash
   python main.py
   ```
3. Point the camera at a braille sign and show your hand in the frame
4. Follow the audio directions to guide your hand to the braille

### Controls
- **`l`**: Lock onto detected braille sign
- **`u`**: Unlock target
- **`q`**: Quit application

## How It Works

1. **Capture**: Webcam streams live video
2. **Detect**: System identifies braille signs and hand position using computer vision
3. **Calculate**: Computes the vector between finger tip and braille center
4. **Guide**: Provides audio directions based on relative positions
5. **Success**: Announces "Centered" when hand reaches the target

## Hardware Notes

This project currently runs on a **laptop** for development and testing. While we initially planned to deploy on a **Raspberry Pi** for portability, we opted to use a laptop for better performance with the deep learning models.

## Project Structure

```
├── main.py                          # Main integration script
├── hand_detection.py                # MediaPipe hand tracking
├── Braille_Detection/               # Braille detection module
│   └── single_braille_file.py
├── voice-main/                      # Audio guidance
│   └── guidance.py
└── requirements.txt                 # Python dependencies
```

## Future Improvements

- Optimize for Raspberry Pi deployment
- Add support for multiple braille signs
- Improve detection accuracy in varying lighting conditions
- Add haptic feedback option

## License

See [LICENSE](LICENSE) file for details.
