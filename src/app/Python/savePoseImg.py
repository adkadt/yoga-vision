import cv2
import mediapipe as mp

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Initialize the camera (0 is usually the default camera)
cap = cv2.VideoCapture(0)

# Check if camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

print("Camera feed started with pose detection!")
print("Press 's' to save the current frame as 'savedPose.jpg' (without pose overlay)")
print("Press 'q' to quit")

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    # If frame is read correctly, ret is True
    if not ret:
        print("Error: Can't receive frame. Exiting...")
        break
    
    # Convert the BGR image to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame with MediaPipe Pose
    results = pose.process(rgb_frame)
    
    # Create a copy of the frame for display with pose overlay
    display_frame = frame.copy()
    
    # Draw pose landmarks on the display frame
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            display_frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
        )
    
    # Display the frame with pose overlay
    cv2.imshow('Camera Feed - Press S to Save, Q to Quit', display_frame)
    
    # Wait for key press (1ms delay)
    key = cv2.waitKey(1) & 0xFF
    
    # Press 's' to save the original frame (without pose overlay)
    if key == ord('s'):
        cv2.imwrite('savedPose.jpg', frame)
        print("Frame saved as 'savedPose.jpg' (without pose overlay)")
    
    # Press 'q' to quit
    elif key == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
pose.close()
print("Camera feed closed")