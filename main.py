import cv2
import time
import os
import sys

# 1. Import Friend's Code (Braille Detection)
# Use absolute path to ensure it works regardless of where command is run
braille_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Braille_Detection')
sys.path.append(braille_dir)

try:
    from single_braille_file import BrailleDetector, calculate_direction, get_voice_command
except ImportError as e:
    print(f"ERROR: Could not import from 'single_braille_file.py'")
    print(f"Looking in: {braille_dir}")
    print(f"Details: {e}")
    sys.exit(1)

# 2. Import My Code (Hand Detection)
from hand_detection import HandNavigator

def main():
    print("="*60)
    print("   INTEGRATED BRAILLE NAVIGATION SYSTEM")
    print("   (MediaPipe Hand Tracking + Computer Vision Braille)")
    print("="*60)
    
    # Initialize Detectors
    print("Initializing Hand Tracker...")
    navigator = HandNavigator()
    
    print("Initializing Braille Detector...")
    braille_detector = BrailleDetector()
    
    # Open Camera (0 = Laptop, 1 = USB Webcam)
    cap = cv2.VideoCapture(1)
    # FORCE LOW RESOLUTION (Simple optimization only)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Audio throttle
    last_speech_time = 0
    SPEECH_INTERVAL = 3.0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        h, w = frame.shape[:2]
        
        # ---------------------------------------------------------
        # STEP 1: Process Hand (My Code)
        # ---------------------------------------------------------
        # This draws the coordinates on the frame too
        frame = navigator.process_frame(frame)
        hand_info = navigator.get_hand_info()
        
        # ---------------------------------------------------------
        # STEP 2: Process Braille (Friend's Code)
        # ---------------------------------------------------------
        # Check if locked
        braille_data = braille_detector.get_locked()
        if not braille_data:
            # Run detection EVERY frame (Reverted behavior)
            braille_data = braille_detector.detect(frame)
            
        # Draw Braille (Manual drawing here to keep it clean on top of hand drawing)
        if braille_data:
            bx, by, bw, bh = braille_data['bbox']
            bcx, bcy = braille_data['center']
            cv2.rectangle(frame, (bx, by), (bx+bw, by+bh), (0, 255, 0), 2)
            cv2.putText(frame, "BRAILLE", (bx, by-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Show lock status
            if braille_detector.get_locked():
                cv2.putText(frame, "LOCKED", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # ---------------------------------------------------------
        # STEP 3: Integration Logic (Guidance)
        # ---------------------------------------------------------
        if hand_info and braille_data:
            # Connect them visually
            hcx, hcy = hand_info['center']
            bcx, bcy = braille_data['center']
            cv2.line(frame, (hcx, hcy), (bcx, bcy), (255, 255, 0), 2)
            
            # Calculate Direction (Using Friend's Math)
            direction_data = calculate_direction(braille_data, hand_info, w, h)
            
            # Get Voice Command (Using Friend's Logic)
            voice_text = get_voice_command(direction_data)
            
            # Display Instructions
            cv2.putText(frame, f"GUIDANCE: {voice_text}", (10, h - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            # Print to console (Simulator for Text-to-Speech)
            current_time = time.time()
            if current_time - last_speech_time > SPEECH_INTERVAL:
                print(f"🗣️  SAY: {voice_text}")
                last_speech_time = current_time
        
        elif not hand_info and braille_data:
             cv2.putText(frame, "Show Hand", (10, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        elif not braille_data:
             cv2.putText(frame, "Finding Braille...", (10, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


        # ---------------------------------------------------------
        # CONTROLS
        # ---------------------------------------------------------
        cv2.imshow("Main Integrated System", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('l') and braille_data:
            braille_detector.lock(braille_data)
            print("Locked on Braille target.")
        elif key == ord('u'):
            braille_detector.unlock()
            print("Unlocked.")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
