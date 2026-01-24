"""
COMPLETE BRAILLE DETECTION WITH COORDINATES
Single file that does everything - replaces braille_webcam_optimized.py
"""

import cv2
import numpy as np

# ========== CONFIGURATION ==========
CAMERA_INDEX = 1  # 0 = laptop camera, 1 = USB camera (change if needed)

# ========== BRAILLE DETECTION CLASS ==========
import os
from ultralytics import YOLO

class BrailleDetector:
    """Detects braille and returns coordinates using YOLOv8"""
    
    def __init__(self):
        self.locked_detection = None
        # Load model - assumes running from root directory
        model_path = os.path.join(os.getcwd(), 'weights', 'yolov8_braille.pt')
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            print(f"Expected path: {model_path}")
            self.model = None
        
    def detect(self, frame):
        """
        Detect braille in frame using YOLO
        """
        if self.model is None:
            return None

        # Run inference
        results = self.model(frame, verbose=False)
        
        best_detection = None
        highest_conf = 0.0
        
        for result in results:
            for box in result.boxes:
                # YOLO boxes are [x1, y1, x2, y2]
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                
                # Filter low confidence
                if conf < 0.4:
                    continue
                
                w = x2 - x1
                h = y2 - y1
                cx = x1 + w // 2
                cy = y1 + h // 2
                area = w * h
                
                if conf > highest_conf:
                    highest_conf = conf
                    best_detection = {
                        'center': (cx, cy),
                        'bbox': (x1, y1, w, h),
                        'area': area,
                        'confidence': conf
                    }

        return best_detection
    
    def lock(self, detection):
        """Lock onto detected braille"""
        self.locked_detection = detection
        
    def unlock(self):
        """Release locked detection"""
        self.locked_detection = None
        
    def get_locked(self):
        """Get locked detection if available"""
        return self.locked_detection


# ========== HELPER FUNCTIONS FOR TEAM INTEGRATION ==========

def calculate_direction(braille_data, hand_data, frame_width, frame_height):
    """
    Calculate which direction hand should move
    
    YOUR TEAMMATES WILL USE THIS!
    
    Args:
        braille_data: Your detection {'center': (cx, cy), ...}
        hand_data: Teammate's detection {'center': (hx, hy), ...}
        frame_width, frame_height: Frame dimensions
        
    Returns:
        {
            'direction': 'left'/'right'/'up'/'down'/'aligned',
            'distance': float (pixels),
            'zone': 'left'/'center'/'right'
        }
    """
    if not braille_data or not hand_data:
        return None
    
    braille_cx, braille_cy = braille_data['center']
    hand_cx, hand_cy = hand_data['center']
    
    # Calculate offsets
    dx = braille_cx - hand_cx  # Positive = braille is right of hand
    dy = braille_cy - hand_cy  # Positive = braille is below hand
    
    # Calculate distance
    distance = np.sqrt(dx**2 + dy**2)
    
    # Determine zone (which third of screen)
    third_width = frame_width / 3
    if braille_cx < third_width:
        zone = 'left'
    elif braille_cx > 2 * third_width:
        zone = 'right'
    else:
        zone = 'center'
    
    # Determine direction
    THRESHOLD = 50  # pixels
    
    if distance < THRESHOLD:
        direction = 'aligned'
    elif abs(dx) > abs(dy):
        direction = 'right' if dx > 0 else 'left'
    else:
        direction = 'down' if dy > 0 else 'up'
    
    return {
        'direction': direction,
        'distance': float(distance),
        'horizontal_offset': int(dx),
        'vertical_offset': int(dy),
        'zone': zone
    }


def get_voice_command(direction_data):
    """
    Convert direction to voice text for ElevenLabs
    
    YOUR TEAMMATE #2 WILL USE THIS!
    
    Returns: String like "Move left, far away"
    """
    if not direction_data:
        return "Scanning for braille"
    
    direction = direction_data['direction']
    distance = direction_data['distance']
    
    # Distance description
    if distance < 50:
        dist_desc = "very close"
    elif distance < 150:
        dist_desc = "close"
    else:
        dist_desc = "far away"
    
    # Voice command
    if direction == 'aligned':
        return "Aligned! Reach forward"
    else:
        return f"Move {direction}, {dist_desc}"


# ========== VISUALIZATION ==========

def draw_detection(frame, braille_data, hand_data=None, direction_data=None):
    """Draw braille detection and coordinates on frame"""
    
    if braille_data:
        # Unpack coordinates
        cx, cy = braille_data['center']
        x, y, w, h = braille_data['bbox']
        
        # Draw bounding box
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        
        # Draw center point
        cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)
        
        # Label with coordinates
        cv2.putText(frame, f"BRAILLE ({cx}, {cy})", (x, y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    if hand_data:
        # Draw hand detection
        hcx, hcy = hand_data['center']
        hx, hy, hw, hh = hand_data['bbox']
        
        cv2.rectangle(frame, (hx, hy), (hx+hw, hy+hh), (255, 0, 255), 2)
        cv2.circle(frame, (hcx, hcy), 8, (255, 0, 255), -1)
        
        cv2.putText(frame, f"HAND ({hcx}, {hcy})", (hx, hy - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
        
        # Draw line connecting hand to braille
        if braille_data:
            bcx, bcy = braille_data['center']
            cv2.line(frame, (hcx, hcy), (bcx, bcy), (255, 255, 0), 2)
    
    if direction_data:
        # Show direction info
        info = [
            f"Direction: {direction_data['direction'].upper()}",
            f"Distance: {int(direction_data['distance'])}px",
            f"Zone: {direction_data['zone']}"
        ]
        
        y_pos = 30
        for text in info:
            cv2.putText(frame, text, (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_pos += 30
    
    return frame


# ========== MAIN PROGRAM ==========

if __name__ == "__main__":
    print("="*60)
    print("       BRAILLE DETECTION WITH COORDINATES")
    print("="*60)
    print("Point camera at braille signs")
    print("\nControls:")
    print("  'q' = Quit")
    print("  'l' = Lock detection")
    print("  'u' = Unlock detection")
    print("="*60 + "\n")
    
    # Initialize detector
    detector = BrailleDetector()
    
    # Open camera
    cap = cv2.VideoCapture(CAMERA_INDEX)
    
    if not cap.isOpened():
        print(f"✗ ERROR: Cannot open camera {CAMERA_INDEX}")
        print(f"\nTry changing CAMERA_INDEX:")
        print(f"  CAMERA_INDEX = 0  # Laptop camera")
        print(f"  CAMERA_INDEX = 1  # USB camera")
        exit()
    
    print(f"✓ Camera {CAMERA_INDEX} opened")
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("✗ Failed to read frame")
            break
        
        h, w = frame.shape[:2]
        
        # Get detection (locked or new)
        braille_data = detector.get_locked()
        if not braille_data:
            braille_data = detector.detect(frame)
        
        # Draw visualization
        frame = draw_detection(frame, braille_data)
        
        # Show lock status
        if detector.get_locked():
            cv2.putText(frame, "LOCKED", (w - 120, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "SCANNING", (w - 150, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
        
        # Print coordinates to console
        if braille_data:
            cx, cy = braille_data['center']
            print(f"\rBraille at: ({cx}, {cy})  ", end='', flush=True)
        
        # Display
        cv2.imshow('Braille Detection', frame)
        
        # Handle keyboard
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('l') and braille_data:
            detector.lock(braille_data)
            print(f"\n✓ Locked at {braille_data['center']}")
        elif key == ord('u'):
            detector.unlock()
            print("\n↻ Unlocked")
    
    cap.release()
    cv2.destroyAllWindows()
    print("\n\nSystem stopped.")


# ========== INTEGRATION EXAMPLE FOR YOUR TEAMMATES ==========
"""
HOW YOUR TEAMMATES USE THIS FILE:

from braille_webcam_optimized import (
    BrailleDetector,
    calculate_direction,
    get_voice_command
)

# Initialize
braille_detector = BrailleDetector()
hand_detector = HandDetector()  # Teammate #1's class

# In main loop:
braille_data = braille_detector.detect(frame)
hand_data = hand_detector.detect(frame)

if braille_data and hand_data:
    # Calculate direction
    direction = calculate_direction(braille_data, hand_data, w, h)
    
    # Get voice command
    voice_text = get_voice_command(direction)
    
    # Teammate #2 speaks it
    speak(voice_text)  # ElevenLabs
"""
