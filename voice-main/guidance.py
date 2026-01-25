import pyttsx3
import time
import threading
import queue

class BrailleGuidance:
    def __init__(self):
        self.speech_queue = queue.Queue()
        self.last_speech_time = 0
        self.min_interval = 2.5
        
        # Start the worker thread
        self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.worker_thread.start()
        print("✓ Voice engine worker started")

    def _speech_worker(self):
        """Dedicated thread for speaking to avoid blocking main loop"""
        while True:
            text = self.speech_queue.get()
            if text is None: break  # Poison pill
            
            try:
                # NUCLEAR OPTION: Re-init engine for EVERY phrase
                # This is the only way to guarantee it doesn't get "stuck"
                engine = pyttsx3.init('sapi5')
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 1.0)
                engine.say(text)
                engine.runAndWait()
                # Explicitly delete to force cleanup
                del engine
            except Exception as e:
                print(f"[ERROR] Speech error: {e}")
            
            self.speech_queue.task_done()

    def speak(self, text):
        """Speaks the text if enough time has passed."""
        current_time = time.time()
        
        # Check throttling
        if current_time - self.last_speech_time > self.min_interval:
            print(f"[DEBUG] Queuing: {text}")
            
            # Clear queue to prioritize newest message? 
            # Ideally yes, we don't want a backlog of old instructions
            with self.speech_queue.mutex:
                self.speech_queue.queue.clear()
            
            self.speech_queue.put(text)
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
    
