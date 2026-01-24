import cv2
import math
import numpy as np
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
        self.hand_bbox = None  # (x, y, w, h)
        
        # 1. Download the model file if not present
        model_name = 'hand_landmarker.task'
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), model_name)
        
        if not os.path.exists(model_path):
            print(f"Downloading {model_name}...")
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            try:
                urllib.request.urlretrieve(url, model_path)
            except:
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
            except:
                self.detector = None
        else:
            self.detector = None

    def process_frame(self, frame):
        """
        Takes a frame, finds the hand, and updates self.finger_pos.
        Returns the modified frame (with debug drawings).
        """
        if self.detector is None:
            return frame

        # Convert to MediaPipe Image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Detect
        result = self.detector.detect(mp_image)
        
        self.finger_pos = None
        self.hand_bbox = None

        if result.hand_landmarks:
            # We only asked for 1 hand
            hand_landmarks = result.hand_landmarks[0]
            
            h, w, c = frame.shape
            
            # Draw connections
            connections = vision.HandLandmarksConnections.HAND_CONNECTIONS
            
            # Map landmarks to pixel coordinates
            px_landmarks = []
            min_x, min_y = w, h
            max_x, max_y = 0, 0

            for landmark in hand_landmarks:
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                px_landmarks.append((cx, cy))
                
                # Update BBox
                min_x = min(min_x, cx)
                min_y = min(min_y, cy)
                max_x = max(max_x, cx)
                max_y = max(max_y, cy)
                
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
            
            # Draw lines
            for connection in connections:
                start_idx = connection.start
                end_idx = connection.end
                if start_idx < len(px_landmarks) and end_idx < len(px_landmarks):
                    cv2.line(frame, px_landmarks[start_idx], px_landmarks[end_idx], (0, 255, 0), 2)

            # Define BBox
            self.hand_bbox = (min_x, min_y, max_x - min_x, max_y - min_y)

            # Get Index Finger Tip (Index 8)
            if len(px_landmarks) > 8:
                tip_x, tip_y = px_landmarks[8]
                self.finger_pos = (tip_x, tip_y)
                # Draw visual indicator for the tip
                cv2.circle(frame, (tip_x, tip_y), 15, (255, 0, 255), cv2.FILLED)
        
        return frame

    def get_hand_info(self):
        """
        Returns dictionary matching the format expected by integrated_hand_braille.py
        """
        if self.finger_pos and self.hand_bbox:
            # Calculate roughly the 'center' of the hand bbox for general tracking,
            # but usually we prefer the finger tip for pointing.
            # However, the friend's code uses 'center' key. 
            # We will return the FINGER TIP as the 'center' because that's what we want to guide!
            return {
                'center': self.finger_pos,   # Guiding the Finger Tip
                'bbox': self.hand_bbox,
                'area': self.hand_bbox[2] * self.hand_bbox[3]
            }
        return None
