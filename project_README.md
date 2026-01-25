# BRAILLE NAVIGATION SYSTEM - Final Project Report

## Project Overview
This project is an **assistive navigation system** designed to help visually impaired users locate braille signage in public spaces. Acting as a "smart guide," it uses computer vision to detect braille signs and the user's hand, providing real-time audio feedback to guide their finger effectively to the text.

**Problem:** Visually impaired individuals often struggle to locate braille signage because signs are small, placed at varying heights, and difficult to find without tactile searching.   
**Solution:** A computer vision-based system that "sees" the braille and the user's hand, offering verbal directional guidance (e.g., "Move hand up", "Move left") until the hand is centered on the braille.

---

## Technical Architecture

### Hardware
*   **Laptop**: Serves as the main processing unit (replacing the initially planned Raspberry Pi for performance reasons).
*   **Webcam**: Captures the live video feed of the environment.
*   **Audio Output**: Laptop speakers provide voice guidance.

*Note: Initial designs included a haptic glove with Arduino and vibration motors, but this was streamlined to an audio-only feedback system for better reliability and lower latency.*

### Software Stack
The project is built in **Python** and leverages the following key libraries:
*   **OpenCV (`cv2`)**: Used for image processing and managing the video feed.
*   **MediaPipe**: Utilized for highly accurate, real-time **Hand Tracking**. It detects landmarks on the user's hand (specifically the index finger tip) to calculate its position relative to the braille.
*   **YOLO / Deep Learning**: Used for robust **Braille Detection**. The system identifies the bounding box of braille text within the camera frame.
*   **pyttsx3**: Provides offline **Text-to-Speech (TTS)** capabilities to vocalize directions.
*   **NumPy**: Handles efficient array operations and geometric calculations for direction logic.

---

## How It Works (The Algorithm)
1.  **Capture**: The webcam captures a live video frame.
2.  **Detection**:
    *   **Braille**: The deep learning model scans the frame for braille signage and returns a bounding box.
    *   **Hand**: MediaPipe detects the user's hand landmarks.
3.  **Calculation**:
    *   The system calculates the center point of the braille sign.
    *   It tracks the position of the user's index finger.
    *   A vector is calculated between the finger tip and the braille center.
4.  **Guidance**:
    *   Based on the vector, the system determines the necessary direction (Up, Down, Left, Right).
    *   **Deadzone Logic**: If the finger is within a small radius of the center, the system announces "Centered" or "Target Reached".
5.  **Feedback**: `pyttsx3` speaks the command to the user (e.g., "Right, far away" or "Down, close").

---

## Setup & Run Instructions

### Prerequisites
*   Python 3.8+
*   Webcam

### Installation
1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install opencv-python mediapipe pyttsx3 numpy
    ```
    *(Note: Additional dependencies for the specific YOLO model may apply)*

### Running the System
1.  Connect your webcam.
2.  Run the main script:
    ```bash
    python main.py
    ```
3.  **Usage**:
    *   Point the camera at a wall with a braille sign.
    *   Raise your hand into the frame.
    *   Result: The system will verbally guide your hand towards the braille sign.

---

## Project Evolution & Constraints
*   **Original Plan**: A fully portable Raspberry Pi wearable with a haptic glove.
*   **Final Implementation**: A laptop-based prototype focusing on software accuracy.
*   **Changes**:
    *   Switched from Arduino haptics to Audio feedback for clearer, more intuitive guidance.
    *   Leveraged **MediaPipe** instead of standard color/contour tracking for robust hand detection.
    *   Running on a Laptop allowed for heavier deep learning models (YOLO) to run at higher frame rates than a standard Raspberry Pi 3/4.

## References
*   [MediaPipe Hands](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker)
*   [OpenCV Documentation](https://docs.opencv.org/)
*   [YOLO Object Detection](https://github.com/ultralytics/ultralytics)