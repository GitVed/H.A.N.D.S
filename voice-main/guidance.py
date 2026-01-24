import pyttsx3

# 1. Initialize the "Voice"
engine = pyttsx3.init()
engine.setProperty('rate', 200) # Speed of speech

def speak(text):
    """Make the computer speak immediately"""
    engine.say(text)
    engine.runAndWait()

def calculate_guidance(hand_x, hand_y, braille_x, braille_y):
    """The math to decide what to say"""
    margin = 40  # How close the hand needs to be (in pixels)

    # Horizontal logic
    if hand_x < braille_x - margin:
        speak("Right")
    elif hand_x > braille_x + margin:
        speak("Left")
    
    # Vertical logic
    elif hand_y < braille_y - margin:
        speak("Down")
    elif hand_y > braille_y + margin:
        speak("Up")
        
    else:
        speak("Found it")

# TEST: Simulate hand at 100 and Braille at 400
calculate_guidance(100, 200, 400, 200)

import pyttsx3
import time

class BrailleGuidance:
    def __init__(self):
        # 1. Setup the Voice Engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 220)  # Speed: slightly fast is better for navigation
        self.engine.setProperty('volume', 1.0) # Full volume
        
        # 2. Timing Variables (Prevents the AI from talking too much)
        self.last_speech_time = 0
        self.speech_delay = 0.8 # Seconds to wait between commands

    def speak(self, text):
        """Checks if enough time has passed, then speaks."""
        current_time = time.time()
        if current_time - self.last_speech_time > self.speech_delay:
            print(f"Directing: {text}") # Visual feedback for you in VS Code
            self.engine.say(text)
            self.engine.runAndWait()
            self.last_speech_time = current_time

    def start_navigation(self):
        """The main loop that will eventually talk to your partners' code."""
        print("System Active. Waiting for detection data...")
        
        try:
            while True:
                # --- THIS IS WHERE THE COORDINATES WILL GO ---
                # For now, we will simulate the logic with a placeholder
                # hx, hy = hand_x, hand_y
                # bx, by = braille_x, braille_y
                
                # EXAMPLE LOGIC:
                # if hand_is_missing:
                #     self.speak("Hand not detected")
                
                pass # This tells Python to keep looping even though it's empty
                
        except KeyboardInterrupt:
            print("System stopped by user.")

# --- RUNNING THE SYSTEM ---
if __name__ == "__main__":
    navigator = BrailleGuidance()
    
    # Test call to make sure your speakers work:
    navigator.speak("System ready. Place your hand on the page.")
    
    # navigator.start_navigation() # Uncomment this when you add coordinates
    
