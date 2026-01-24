import cv2

def list_cameras():
    print("Searching for cameras...")
    available_cameras = []
    for i in range(5):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW) # standard Windows backend
        if cap.isOpened():
            # Try to get the name (backend dependent, might just return true)
            print(f"✅ Camera Index {i}: FOUND")
            available_cameras.append(i)
            cap.release()
        else:
            print(f"❌ Camera Index {i}: Not found")
    
    print("\nSummary:")
    if not available_cameras:
        print("No cameras found!")
    else:
        print(f"Available indices: {available_cameras}")
        print("Try changing 'cap = cv2.VideoCapture(INDEX)' in main.py to one of these.")

if __name__ == "__main__":
    list_cameras()
