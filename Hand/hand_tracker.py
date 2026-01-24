"""
HAND TRACKING MODULE
Detects hand position and guides it toward braille using haptic feedback
"""

import cv2
import numpy as np

class HandTracker:
    """
    Detects hand in frame using skin color detection and contour analysis.
    Works in various lighting conditions.
    """
    
    def __init__(self):
        # Skin color range in HSV
        # These values work for most skin tones
        self.lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        self.upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Minimum hand size (to filter noise)
        self.min_hand_area = 3000
        
    def detect_hand(self, frame):
        """
        Detect hand in frame.
        
        Returns:
            dict or None: {
                'center': (x, y),      # Hand center position
                'bbox': (x, y, w, h),  # Bounding box
                'area': int            # Contour area
            }
        """
        # Convert to HSV for better skin detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create mask for skin color
        mask = cv2.inRange(hsv, self.lower_skin, self.upper_skin)
        
        # Noise reduction
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=2)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        
        # Find contours
        contours, _ = cv2.findContours(
            mask, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        if not contours:
            return None
        
        # Get largest contour (most likely the hand)
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        
        # Filter out small detections (noise)
        if area < self.min_hand_area:
            return None
        
        # Get bounding box
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Calculate center
        center_x = x + w // 2
        center_y = y + h // 2
        
        return {
            'center': (center_x, center_y),
            'bbox': (x, y, w, h),
            'area': area
        }
    
    def draw_hand_detection(self, frame, hand_info):
        """Draw hand detection visualization"""
        if not hand_info:
            return frame
        
        x, y, w, h = hand_info['bbox']
        center_x, center_y = hand_info['center']
        
        # Draw bounding box
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 255), 2)
        
        # Draw center point
        cv2.circle(frame, (center_x, center_y), 8, (255, 0, 255), -1)
        
        # Label
        cv2.putText(frame, "HAND", (x, y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
        
        return frame


def calculate_hand_guidance(hand_info, braille_bbox, frame_width):
    """
    Calculate which motor to vibrate based on hand position relative to braille.
    
    Args:
        hand_info: Hand detection result
        braille_bbox: Braille bounding box (x, y, w, h)
        frame_width: Width of frame
        
    Returns:
        dict: {
            'motor': 'L'/'C'/'R',      # Which motor to activate
            'intensity': 1/2/3,         # How strong (distance-based)
            'message': str              # Audio feedback
        }
    """
    if not hand_info or not braille_bbox:
        return None
    
    hand_x, hand_y = hand_info['center']
    braille_x, braille_y, braille_w, braille_h = braille_bbox
    
    # Braille center
    braille_center_x = braille_x + braille_w // 2
    braille_center_y = braille_y + braille_h // 2
    
    # Calculate horizontal offset
    dx = braille_center_x - hand_x
    dy = braille_center_y - hand_y
    
    # Calculate distance
    distance = np.sqrt(dx**2 + dy**2)
    
    # Determine intensity based on distance
    if distance < 50:
        intensity = 3
        dist_text = "very close"
    elif distance < 150:
        intensity = 2
        dist_text = "close"
    else:
        intensity = 1
        dist_text = "far"
    
    # Determine which motor (divide screen into thirds)
    third_width = frame_width / 3
    
    if braille_center_x < third_width:
        motor = 'L'
        direction = "left"
    elif braille_center_x > 2 * third_width:
        motor = 'R'
        direction = "right"
    else:
        motor = 'C'
        direction = "center"
    
    # Check if hand is aligned (within tolerance)
    if abs(dx) < 40 and abs(dy) < 40:
        return {
            'motor': 'C',
            'intensity': 3,
            'message': "Aligned! Touch the braille",
            'aligned': True
        }
    
    return {
        'motor': motor,
        'intensity': intensity,
        'message': f"Braille is {dist_text}, move hand {direction}",
        'aligned': False
    }


# ========== TEST THE HAND TRACKER ==========
if __name__ == "__main__":
    tracker = HandTracker()
    cap = cv2.VideoCapture(0)
    
    print("="*60)
    print("HAND TRACKER TEST")
    print("="*60)
    print("Show your hand to the camera")
    print("Press 'q' to quit")
    print("="*60)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect hand
        hand_info = tracker.detect_hand(frame)
        
        # Draw detection
        if hand_info:
            frame = tracker.draw_hand_detection(frame, hand_info)
            center_x, center_y = hand_info['center']
            print(f"Hand detected at ({center_x}, {center_y})")
        else:
            cv2.putText(frame, "No hand detected", (10, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        cv2.imshow('Hand Tracker Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
