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
        # Setup the Voice Engine with Windows-compatible settings
        try:
            self.engine = pyttsx3.init('sapi5')  # Explicitly use Windows SAPI5
            self.engine.setProperty('rate', 180)  # Slower for clarity
            self.engine.setProperty('volume', 1.0)  # Full volume
            
            # Get available voices and set to default
            voices = self.engine.getProperty('voices')
            if voices:
                self.engine.setProperty('voice', voices[0].id)
            
            print("✓ Voice engine initialized")
        except Exception as e:
            print(f"⚠ Voice engine failed: {e}")
            self.engine = None

    def speak(self, text):
        """Speaks the given text immediately without throttling."""
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                # If there's an error, try to reinitialize
                try:
                    self.engine = pyttsx3.init('sapi5')
                    self.engine.say(text)
                    self.engine.runAndWait()
                except:
                    pass  # Silent fail

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
    
