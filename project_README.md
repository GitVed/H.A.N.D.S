BRAILLE NAVIGATION SYSTEM - Executive Summary
Project Overview
A wearable assistive device that helps blind people locate braille signs independently. The system uses computer vision to detect braille text, then guides the user to it through audio directions and haptic vibrations on a glove.
Problem: Blind people can't locate braille signs because they're small, high up, and hard to find without sight.
Solution: Point-and-find system with real-time guidance via voice + vibration motors.

Hardware Components
ComponentPurposeStatusLaptop (current)Runs computer vision, processes video, controls system✅ Using nowRaspberry Pi (later)Portable version - same role as laptop⏳ TroubleshootingLogitech WebcamCaptures video of environment to detect braille✅ Have itArduino Uno R3Controls vibration motors based on laptop commands✅ Have it3x Coin Vibration MotorsHaptic feedback (left/right/centered directions)✅ From starter kitTransistors (TIP120 or 2N2222)Allow Arduino to safely control motors✅ From starter kitResistors (1kΩ)Protect transistor circuits✅ From starter kitBreadboard + WiresCircuit assembly✅ From starter kitGlove/FabricWearable mount for motors🔨 Need to build

Software & Tools
Installed So Far:
bashpip install opencv-python pyserial pyttsx3 numpy pillow
git clone [dotneuralnet repo]
```

### **What Each Does:**
- **opencv-python**: Computer vision library for webcam capture and image processing
- **pyserial**: Communicates with Arduino via USB serial connection
- **pyttsx3**: Text-to-speech for audio guidance (offline, no API needed)
- **numpy**: Math operations for image processing
- **pillow**: Image manipulation utilities
- **dotneuralnet**: Pre-trained braille detection model (currently exploring)

### **Additional Software Needed:**
- **Arduino IDE** - Upload code to Arduino Uno ([download](https://www.arduino.cc/en/software))
- **Git** - Already have (used to clone repo)
- **Python 3.7+** - Already have

---

## **System Architecture**
```
┌──────────────┐
│   LAPTOP     │ ← Running everything for now
│              │
│ [Webcam USB] │ ← Logitech camera captures video
│      ↓       │
│  [Python]    │ ← Detects braille, calculates direction
│      ↓       │
│ [Audio Out]  │ ← Speaks "move left", "centered", etc.
│      ↓       │
│ [USB Serial] │ ← Sends motor commands to Arduino
└──────┬───────┘
       │
       ↓
┌──────────────┐
│   ARDUINO    │
│   UNO R3     │
│      ↓       │
│ [3 Motors]   │ ← Vibrate left/right/center
└──────────────┘
Later (when Pi works):
Just replace "LAPTOP" with "RASPBERRY PI" - same code, same connections.

How It Works - User Flow

User wears glove with 3 vibration motors
Points camera (webcam) at wall/door/elevator
System detects braille using computer vision
Calculates direction: Is braille left/right/up/down from center?
Audio speaks: "Move right, far away"
Motors vibrate: Right motor buzzes
User adjusts camera position
Repeat until braille is centered
Success! All motors pulse, audio says "Centered! Reach forward"
User's hand is now positioned to touch the braille


COMPLETE STEP-BY-STEP BUILD GUIDE

STEP 1: Software Setup (15 minutes)
1.1 Verify Python Installation
bashpython --version
# Should show Python 3.7 or higher
1.2 Install Dependencies (already done)
bashpip install opencv-python pyserial pyttsx3 numpy pillow
1.3 Test Webcam Works
Create file test_webcam.py:
pythonimport cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Webcam not found")
    exit()

print("Webcam working! Press 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    cv2.imshow('Webcam Test', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
Run: python test_webcam.py
Expected: Window shows live webcam feed

STEP 2: Braille Detection Setup (30 minutes)
2.1 Explore DotNeuralNet Repo
bashcd dotneuralnet  # Or whatever the repo name is
ls
Look for:

detect.py or similar detection script
model/ folder with trained weights
README.md with usage instructions

2.2 Test Braille Detection (if repo has working code)
bash# Try running their detection script
python detect_braille.py --help
If it works: Great! Use their detector.
If it's broken/unclear: Use our backup detector (next step).
2.3 Create Backup Detector (RECOMMENDED for hackathon reliability)
Create file braille_detector.py:
pythonimport cv2
import numpy as np

class BrailleDetector:
    """
    Detects braille signs using high-contrast edge detection.
    Works for most bathroom signs, elevator buttons, room numbers.
    """
    
    def detect(self, frame):
        """
        Input: OpenCV frame (BGR image)
        Output: List of detections [{'bbox': (x,y,w,h), 'confidence': float}]
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Adaptive threshold for different lighting conditions
        thresh = cv2.adaptiveThreshold(
            gray, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Find contours (edges of braille signs)
        contours, _ = cv2.findContours(
            thresh, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        results = []
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by size (braille signs are medium-sized)
            if 1000 < area < 80000:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check aspect ratio (signs are roughly rectangular)
                aspect_ratio = float(w) / h if h > 0 else 0
                
                if 0.2 < aspect_ratio < 6:
                    results.append({
                        'bbox': (x, y, w, h),
                        'confidence': 0.85
                    })
        
        # Return largest detection (most likely the sign)
        if results:
            largest = max(results, key=lambda r: r['bbox'][2] * r['bbox'][3])
            return [largest]
        
        return []

# TEST THE DETECTOR
if __name__ == "__main__":
    detector = BrailleDetector()
    cap = cv2.VideoCapture(0)
    
    print("Point camera at braille sign. Press 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        results = detector.detect(frame)
        
        # Draw detections
        for result in results:
            x, y, w, h = result['bbox']
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
            cv2.putText(frame, "BRAILLE DETECTED", (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow('Braille Detector Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
```

**Run:** `python braille_detector.py`  
**Test:** Point camera at bathroom signs, text on paper, elevator buttons  
**Expected:** Green box appears around high-contrast objects

---

## **STEP 3: Arduino Hardware Setup (45 minutes)**

### 3.1 Download Arduino IDE
- Go to https://www.arduino.cc/en/software
- Download for your OS
- Install

### 3.2 Wire the Motors

**Circuit for ONE motor (repeat 3 times for 3 motors):**
```
Arduino 5V ──┐
             │
        ┌────┴────┐
        │  MOTOR  │
        │  (+)    │
        └────┬────┘
             │
     Collector (C)
        ┌────┴────┐
        │         │
        │ TIP120  │  ← Transistor
        │         │
        └─┬─────┬─┘
Base (B)─┘     └─ Emitter (E)
  │               │
  │               └─── Arduino GND
  │
1kΩ Resistor
  │
Arduino Pin 9
Full wiring for 3 motors:
Arduino Pin→ Resistor →Transistor BaseTransistor CollectorTransistor EmitterPin 91kΩBaseMotor 1 (+)GNDPin 101kΩBaseMotor 2 (+)GNDPin 111kΩBaseMotor 3 (+)GND
Also connect:

Arduino 5V → All motor (+) wires (through transistor collectors)
Arduino GND → All transistor emitters
Arduino GND → All motor (-) wires

Visual check:

3 transistors on breadboard
3 resistors connecting Arduino pins to transistor bases
3 motors connected to collectors
Common ground rail

3.3 Upload Arduino Code
Open Arduino IDE → New Sketch → Paste this:
cpp// BRAILLE NAVIGATION - HAPTIC GLOVE CONTROLLER
// Receives serial commands from laptop, controls 3 motors

const int MOTOR_LEFT = 9;
const int MOTOR_CENTER = 10;
const int MOTOR_RIGHT = 11;

void setup() {
  pinMode(MOTOR_LEFT, OUTPUT);
  pinMode(MOTOR_CENTER, OUTPUT);
  pinMode(MOTOR_RIGHT, OUTPUT);
  
  Serial.begin(9600);
  
  // Startup confirmation (all motors buzz)
  startupSequence();
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    switch(command) {
      case 'L':  // Move LEFT
        vibrateMotor(MOTOR_LEFT, 300);
        break;
        
      case 'R':  // Move RIGHT
        vibrateMotor(MOTOR_RIGHT, 300);
        break;
        
      case 'U':  // Move UP (both side motors)
        vibrateMotor(MOTOR_LEFT, 150);
        delay(50);
        vibrateMotor(MOTOR_RIGHT, 150);
        break;
        
      case 'D':  // Move DOWN
        vibrateMotor(MOTOR_CENTER, 300);
        break;
        
      case 'C':  // CENTERED! Success pattern
        successPattern();
        break;
        
      case '1':  // Distance: FAR (weak pulse)
        vibrateMotor(MOTOR_CENTER, 100);
        break;
        
      case '2':  // Distance: CLOSE (medium pulse)
        vibrateMotor(MOTOR_CENTER, 200);
        break;
        
      case '3':  // Distance: VERY CLOSE (strong pulse)
        vibrateMotor(MOTOR_CENTER, 400);
        break;
    }
  }
}

void vibrateMotor(int motorPin, int durationMs) {
  digitalWrite(motorPin, HIGH);
  delay(durationMs);
  digitalWrite(motorPin, LOW);
}

void successPattern() {
  // All motors pulse together 3 times
  for(int i = 0; i < 3; i++) {
    digitalWrite(MOTOR_LEFT, HIGH);
    digitalWrite(MOTOR_CENTER, HIGH);
    digitalWrite(MOTOR_RIGHT, HIGH);
    delay(200);
    
    digitalWrite(MOTOR_LEFT, LOW);
    digitalWrite(MOTOR_CENTER, LOW);
    digitalWrite(MOTOR_RIGHT, LOW);
    delay(200);
  }
}

void startupSequence() {
  // Sequential startup (left → center → right)
  vibrateMotor(MOTOR_LEFT, 200);
  delay(100);
  vibrateMotor(MOTOR_CENTER, 200);
  delay(100);
  vibrateMotor(MOTOR_RIGHT, 200);
}
Upload steps:

Tools → Board → Arduino Uno
Tools → Port → Select your Arduino (COM3, /dev/ttyACM0, etc.)
Click Upload button (→)
Wait for "Done uploading"

Expected: Motors should buzz in sequence (left-center-right) on startup.
3.4 Test Arduino from Python
Create file test_arduino.py:
pythonimport serial
import time

# CHANGE THIS to your Arduino port!
# Windows: 'COM3', 'COM4', etc.
# Mac/Linux: '/dev/ttyACM0', '/dev/ttyUSB0', etc.
ARDUINO_PORT = 'COM3'

try:
    arduino = serial.Serial(ARDUINO_PORT, 9600, timeout=1)
    time.sleep(2)  # Wait for Arduino to initialize
    
    print("Testing motors...")
    
    print("  → Left motor")
    arduino.write(b'L')
    time.sleep(1)
    
    print("  → Right motor")
    arduino.write(b'R')
    time.sleep(1)
    
    print("  → Center motor")
    arduino.write(b'D')
    time.sleep(1)
    
    print("  → Success pattern")
    arduino.write(b'C')
    time.sleep(2)
    
    print("✓ All motors working!")
    arduino.close()
    
except serial.SerialException as e:
    print(f"ERROR: Could not connect to Arduino on {ARDUINO_PORT}")
    print(f"Details: {e}")
    print("\nTroubleshooting:")
    print("1. Check Arduino is plugged in via USB")
    print("2. Verify port name in Device Manager (Windows) or ls /dev/tty.* (Mac)")
    print("3. Make sure Arduino IDE isn't open (it locks the port)")
Run: python test_arduino.py
Expected: Each motor vibrates in sequence, then success pattern

STEP 4: Integration - Full System (30 minutes)
4.1 Create Main Application
Create file braille_navigation.py:
python"""
BRAILLE NAVIGATION SYSTEM
Laptop version - uses webcam + Arduino for haptic feedback
"""

import cv2
import serial
import time
import pyttsx3
import threading
from braille_detector import BrailleDetector

# ========== CONFIGURATION ==========
ARDUINO_PORT = 'COM3'  # ← CHANGE THIS to your port!
CAMERA_INDEX = 0
SPEECH_INTERVAL = 2  # Seconds between audio updates
DEADZONE = 60  # Pixels - how close to center counts as "centered"

# ========== INITIALIZE COMPONENTS ==========
print("Initializing Braille Navigation System...")

# Braille detector
detector = BrailleDetector()
print("✓ Detector loaded")

# Webcam
cap = cv2.VideoCapture(CAMERA_INDEX)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("✗ ERROR: Cannot open webcam")
    exit()
print("✓ Webcam connected")

# Arduino
try:
    arduino = serial.Serial(ARDUINO_PORT, 9600, timeout=1)
    time.sleep(2)
    print("✓ Arduino connected")
except Exception as e:
    print(f"⚠ WARNING: Arduino not connected ({e})")
    print("  Continuing without haptic feedback...")
    arduino = None

# Text-to-speech
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)
print("✓ Text-to-speech ready")

last_speech_time = 0

# ========== HELPER FUNCTIONS ==========

def speak_async(text):
    """Non-blocking speech"""
    def _speak():
        try:
            engine.say(text)
            engine.runAndWait()
        except:
            pass
    threading.Thread(target=_speak, daemon=True).start()

def get_direction_command(bbox, frame_width, frame_height):
    """
    Calculate guidance based on braille position in frame.
    
    Returns:
        voice_msg (str): What to say to user
        motor_cmd (str): Command to send Arduino (L/R/U/D/C)
        dist_level (str): Distance indicator (1/2/3)
    """
    x, y, w, h = bbox
    
    # Calculate center of detected braille
    center_x = x + w/2
    center_y = y + h/2
    
    # Frame center
    frame_center_x = frame_width / 2
    frame_center_y = frame_height / 2
    
    # Calculate offset from center
    dx = center_x - frame_center_x
    dy = center_y - frame_center_y
    
    # Estimate distance based on bounding box size
    box_area = w * h
    
    if box_area > 40000:
        distance = "very close"
        dist_level = '3'
    elif box_area > 15000:
        distance = "close"
        dist_level = '2'
    else:
        distance = "far away"
        dist_level = '1'
    
    # Determine direction (with deadzone for stability)
    if abs(dx) < DEADZONE and abs(dy) < DEADZONE:
        return "Centered! Reach forward", 'C', dist_level
    
    # Prioritize horizontal movement (easier for user)
    if abs(dx) > abs(dy):
        if dx < -DEADZONE:
            return f"Move right, {distance}", 'R', dist_level
        elif dx > DEADZONE:
            return f"Move left, {distance}", 'L', dist_level
    else:
        if dy < -DEADZONE:
            return f"Move down, {distance}", 'D', dist_level
        elif dy > DEADZONE:
            return f"Move up, {distance}", 'U', dist_level
    
    return f"Adjusting, {distance}", dist_level, dist_level

def draw_ui(frame, bbox=None, voice_msg="Scanning..."):
    """Draw user interface on frame"""
    
    # Draw crosshair at center
    h, w = frame.shape[:2]
    center_x, center_y = w//2, h//2
    
    cv2.line(frame, (center_x - 30, center_y), 
             (center_x + 30, center_y), (0, 0, 255), 2)
    cv2.line(frame, (center_x, center_y - 30), 
             (center_x, center_y + 30), (0, 0, 255), 2)
    
    # Draw deadzone circle
    cv2.circle(frame, (center_x, center_y), DEADZONE, (255, 0, 0), 2)
    
    # Draw detection box if found
    if bbox:
        x, y, w, h = bbox
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        
        # Draw line from detection to center
        det_center_x = x + w//2
        det_center_y = y + h//2
        cv2.line(frame, (det_center_x, det_center_y), 
                (center_x, center_y), (255, 255, 0), 2)
    
    # Status text
    cv2.putText(frame, voice_msg, (10, 40),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, 
               (0, 255, 0) if bbox else (0, 0, 255), 2)
    
    return frame

# ========== MAIN LOOP ==========

print("\n" + "="*60)
print("           BRAILLE NAVIGATION SYSTEM ACTIVE")
print("="*60)
print("Point camera at braille signs (bathroom, elevator, etc.)")
print("Press 'q' to quit")
print("="*60 + "\n")

try:
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("ERROR: Failed to read from camera")
            break
        
        # Detect braille
        results = detector.detect(frame)
        
        if results and len(results) > 0:
            # Get first detection
            bbox = results[0]['bbox']
            
            # Calculate direction
            voice_msg, motor_cmd, dist_level = get_direction_command(
                bbox, frame.shape[1], frame.shape[0]
            )
            
            # Send motor command to Arduino
            if arduino and motor_cmd:
                try:
                    arduino.write(motor_cmd.encode())
                    arduino.write(dist_level.encode())
                except:
                    pass
            
            # Audio guidance (throttled to avoid spam)
            current_time = time.time()
            if current_time - last_speech_time > SPEECH_INTERVAL:
                speak_async(voice_msg)
                last_speech_time = current_time
                print(f"🎯 {voice_msg}")
            
            # Draw UI
            frame = draw_ui(frame, bbox, voice_msg)
            
        else:
            # No braille detected
            frame = draw_ui(frame, None, "Scanning for braille...")
        
        # Display
        cv2.imshow('Braille Navigation System', frame)
        
        # Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    if arduino:
        arduino.close()
    print("System stopped.")
4.2 Run the Full System
Before running:

✓ Arduino is plugged in and motors are wired
✓ Webcam is plugged in
✓ Update ARDUINO_PORT in code to your actual port

Run:
bashpython braille_navigation.py
```

**Test:**
1. Point camera at bathroom sign with braille
2. Should see green box around sign
3. Should hear "Move left/right, far away"
4. Motors should vibrate in that direction
5. Adjust camera position
6. When centered, all motors pulse and voice says "Centered!"

---

## **STEP 5: Build the Glove (30 minutes)**

### 5.1 Materials
- Old glove or stretchy fabric strip
- Thin wires (extend Arduino to glove)
- Tape or hot glue
- Velcro strips

### 5.2 Motor Placement

**Option A: On palm of glove**
```
        [Motor LEFT]
             |
       [Motor CENTER]
             |
        [Motor RIGHT]
Option B: On forearm (easier)

Attach motors in a row on fabric strip
Wrap around forearm with velcro

5.3 Wiring

Extend wires from breadboard to glove (~3 feet)
Use thin, flexible wires
Label each wire (L, C, R, GND)
Secure with tape so they don't pull out

5.4 Test Wearability

Put on glove
Run python test_arduino.py
Motors should still vibrate
Make sure it's comfortable


STEP 6: Demo Preparation (30 minutes)
6.1 Find Test Locations
Walk around and find:

Bathroom signs with braille
Elevator buttons
Room number plates
Exit signs

Take photos for backup (in case live demo fails).
6.2 Practice Demo Script
Opening (30 seconds):
"Blind people can't find braille signs. They're too small and high up. Our system is like a metal detector for braille - it guides you directly to it."
Live Demo (2 minutes):

Show problem: Point at wall randomly
Show solution: System detects braille
Follow guidance: Move camera as directed
Success: "Centered!" - reach forward and touch braille
BONUS: Do it blindfolded!

Impact (30 seconds):
"This enables independent navigation in any building. No more asking for help, no more searching walls blindly."
6.3 Backup Plans
If Arduino fails:

Demo still works with just audio + visual feedback
Show circuit and explain what it would do

If detection fails:

Use pre-recorded video showing it working
Explain algorithm and show code

If camera fails:

Use laptop camera instead of external webcam


STEP 7: Tomorrow - Transfer to Raspberry Pi
Once Pi is working:

Copy all Python files to Pi:

bashscp *.py pi@raspberry_pi_ip:/home/pi/braille_nav/

Change only 2 lines in braille_navigation.py:

pythonARDUINO_PORT = '/dev/ttyACM0'  # Instead of COM3
CAMERA_INDEX = 0  # Should work same

Run on Pi:

bashpython3 braille_navigation.py
```

**That's it!** Everything else is identical.

---

## **Quick Reference - Files You'll Have**
```
braille_project/
├── braille_detector.py         ← Braille detection class
├── braille_navigation.py       ← Main application
├── test_webcam.py             ← Test camera works
├── test_arduino.py            ← Test motors work
└── arduino_haptic_glove/      ← Arduino sketch folder
    └── arduino_haptic_glove.ino

Troubleshooting
ProblemSolution"Cannot open webcam"Try CAMERA_INDEX = 1 or 2"Serial port not found"Check Arduino IDE → Tools → PortMotors don't vibrateCheck transistor wiring, try digitalWrite testNo braille detectedPoint at high-contrast signs, adjust lightingAudio not workingRun pip install pyttsx3 again, check speakers

What You Should Have Working Tonight
✅ Webcam detecting braille signs
✅ Audio saying directions
✅ Motors vibrating correctly
✅ Full working demo on laptop
✅ Glove assembled
✅ Demo script practiced
Tomorrow: Just transfer to Pi and you're done!