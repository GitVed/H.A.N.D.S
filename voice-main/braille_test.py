import pyttsx3

engine = pyttsx3.init()
braille_x, braille_y = 400, 200 
margin = 50 

print("--- Priority System Active ---")

while True:
    try:
        hand_x = int(input("Enter Hand X: "))
        hand_y = int(input("Enter Hand Y: "))

        # STEP 1: Fix Horizontal (Left/Right)
        if hand_x < braille_x - margin:
            direction = "Move Right"
        elif hand_x > braille_x + margin:
            direction = "Move Left"
        
        # STEP 2: If X is okay, fix Vertical (Up/Down)
        elif hand_y < braille_y - margin:
            direction = "Move Down"
        elif hand_y > braille_y + margin:
            direction = "Move Up"
        
        # STEP 3: Only if BOTH are within the margin
        else:
            direction = "Found it"

        print(f"Instruction: {direction}")
        engine.say(direction)
        engine.runAndWait()

    except ValueError:
        print("Please enter a number!")
        


