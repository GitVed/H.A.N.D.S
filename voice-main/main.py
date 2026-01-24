import pyttsx3
import time

engine = pyttsx3.init()
engine.setProperty('rate', 200)

# This variable remembers what the computer said last
last_direction = ""

print("System Active. Navigate the hand to the Braille.")

while True:
    # --- TEST COORDINATES ---
    hand_x, hand_y = 300, 500       # Hand is at the bottom
    braille_x, braille_y = 300, 200 # Braille is at the top
    # -------------------------

    margin = 50 
    current_direction = ""

    # 1. Decide the direction
    if hand_x < braille_x - margin:
        current_direction = "Right"
    elif hand_x > braille_x + margin:
        current_direction = "Left"
    elif hand_y < braille_y - margin:
        current_direction = "Down"
    elif hand_y > braille_y + margin:
        current_direction = "Up"
    else:
        current_direction = "Found it"

    # 2. Only speak if the direction has CHANGED
    if current_direction != last_direction:
        print(f"New Instruction: {current_direction}")
        engine.say(current_direction)
        engine.runAndWait()
        
        # Update our memory
        last_direction = current_direction

    # 3. If "Found it", stop the program
    if current_direction == "Found it":
        print("Target reached. Closing system.")
        break

    # Check very often (half a second) but it only talks when needed!
    time.sleep(0.5)
