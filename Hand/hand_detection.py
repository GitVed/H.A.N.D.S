import cv2
import math
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import urllib.request

class HandNavigator:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        self.finger_pos = None
        
        # 1. Download the model file if not present
        model_name = 'hand_landmarker.task'
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), model_name)
        
        if not os.path.exists(model_path):
            print(f"Downloading {model_name}...")
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            try:
                urllib.request.urlretrieve(url, model_path)
                print("Download complete.")
            except Exception as e:
                print(f"Error downloading model: {e}")
                # Create a dummy file to prevent constant redownload attempts if offline, 
                # though it will fail later
                pass

        # 2. Initialize the HandLandmarker
        if os.path.exists(model_path):
            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                num_hands=1,
                min_hand_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            try:
                self.detector = vision.HandLandmarker.create_from_options(options)
                print("HandLandmarker initialized successfully.")
            except Exception as e:
                print(f"Failed to init HandLandmarker: {e}")
                self.detector = None
        else:
            print("Model file not found.")
            self.detector = None

    def process_frame(self, frame):
        """
        Takes a frame, finds the hand, draws landmarks, 
        and updates self.finger_pos.
        """
        if self.detector is None:
            cv2.putText(frame, "Model Missing", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            return frame

        # Convert to MediaPipe Image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Detect
        result = self.detector.detect(mp_image)
        
        self.finger_pos = None

        if result.hand_landmarks:
            # We only asked for 1 hand
            hand_landmarks = result.hand_landmarks[0]
            
            # Draw landmarks (Manual drawing since solutions.drawing_utils might be missing)
            h, w, c = frame.shape
            
            # Draw connections
            connections = vision.HandLandmarksConnections.HAND_CONNECTIONS
            # connections is a set of (start, end) tuples
            
            # Map landmarks to pixel coordinates
            px_landmarks = []
            for landmark in hand_landmarks:
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                px_landmarks.append((cx, cy))
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
            
            # Draw lines
            for connection in connections:
                start_idx = connection.start
                end_idx = connection.end
                if start_idx < len(px_landmarks) and end_idx < len(px_landmarks):
                    cv2.line(frame, px_landmarks[start_idx], px_landmarks[end_idx], (0, 255, 0), 2)

            # Get Index Finger Tip (Index 8)
            if len(px_landmarks) > 8:
                tip_x, tip_y = px_landmarks[8]
                self.finger_pos = (tip_x, tip_y)
                # Draw visual indicator for the tip
                cv2.circle(frame, (tip_x, tip_y), 15, (255, 0, 255), cv2.FILLED)
        
        return frame

    def get_guidance(self, target_pos):
        if self.finger_pos is None:
            return ("No Hand Detected", None)
        
        if target_pos is None:
            return ("No Braille Detected", None)

        fx, fy = self.finger_pos
        tx, ty = target_pos

        distance = math.sqrt((tx - fx)**2 + (ty - fy)**2)

        if distance < 30:
            return ("ARRIVED", distance)

        dx = tx - fx
        dy = ty - fy

        if abs(dx) > abs(dy):
            direction = "Right" if dx > 0 else "Left"
        else:
            direction = "Down" if dy > 0 else "Up"
            
        return (f"Move {direction}", distance)
