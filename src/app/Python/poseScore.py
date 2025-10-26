import cv2
import mediapipe as mp
import numpy as np
import math
import os

module_path = os.path.abspath(__file__)
module_directory = os.path.dirname(module_path)
print(module_directory)

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Load the saved pose image
saved_image = cv2.imread(f'{module_directory}/std_poses/savedPose.jpg')

if saved_image is None:
    print("Error: Could not load 'savedPose.jpg'. Make sure the file exists.")
    exit()

# Process the saved image to get pose landmarks
saved_rgb = cv2.cvtColor(saved_image, cv2.COLOR_BGR2RGB)
saved_results = pose.process(saved_rgb)

# Draw pose on saved image
saved_display = saved_image.copy()
if saved_results.pose_landmarks:
    mp_drawing.draw_landmarks(
        saved_display,
        saved_results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2),
        mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=2)
    )
    print("Saved pose detected successfully!")
else:
    print("Warning: No pose detected in saved image")

# Initialize the camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

print("Camera feed started!")
print("Green overlay = Live pose")
print("Blue overlay = Saved pose reference")
print("Controls:")
print("  Arrow keys: Move saved pose overlay")
print("  '+' / '=': Scale up saved pose")
print("  '-' / '_': Scale down saved pose")
print("  'r': Reset position and scale")
print("  'q': Quit")

# Offset and scale variables for saved pose
offset_x = 0.0
offset_y = 0.0
scale = 1.0
move_step = 0.01  # Movement step (as fraction of image size)
scale_step = 0.05  # Scale step

def calculate_pose_similarity(landmarks1, landmarks2):
    """
    Calculate similarity between two poses based on landmark distances.
    Returns a score from 0-100, where 100 is a perfect match.
    """
    if landmarks1 is None or landmarks2 is None:
        return 0.0
    
    total_distance = 0.0
    num_landmarks = len(landmarks1.landmark)
    
    for i in range(num_landmarks):
        lm1 = landmarks1.landmark[i]
        lm2 = landmarks2.landmark[i]
        
        # Calculate Euclidean distance between corresponding landmarks
        distance = math.sqrt(
            (lm1.x - lm2.x) ** 2 + 
            (lm1.y - lm2.y) ** 2 + 
            (lm1.z - lm2.z) ** 2
        )
        total_distance += distance
    
    # Average distance per landmark
    avg_distance = total_distance / num_landmarks
    
    # Convert to similarity score (0-100)
    # Assuming max reasonable distance is 1.0 (full diagonal of normalized space)
    similarity = max(0, 100 - (avg_distance * 100))
    
    return similarity

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    if not ret:
        print("Error: Can't receive frame. Exiting...")
        break
    
    # Convert the BGR image to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the live frame with MediaPipe Pose
    live_results = pose.process(rgb_frame)
    
    # Create display frame
    display_frame = frame.copy()
    
    # Draw SAVED pose landmarks on the live frame (in BLUE) with offset and scale
    if saved_results.pose_landmarks:
        # Create a copy of landmarks with offset and scale applied
        adjusted_landmarks = mp_pose.PoseLandmark
        landmark_list = []
        
        for landmark in saved_results.pose_landmarks.landmark:
            adjusted_landmark = type(landmark)()
            # Apply scale from center (0.5, 0.5)
            adjusted_landmark.x = (landmark.x - 0.5) * scale + 0.5 + offset_x
            adjusted_landmark.y = (landmark.y - 0.5) * scale + 0.5 + offset_y
            adjusted_landmark.z = landmark.z * scale
            adjusted_landmark.visibility = landmark.visibility
            landmark_list.append(adjusted_landmark)
        
        # Create new landmark list
        adjusted_pose = type(saved_results.pose_landmarks)()
        adjusted_pose.landmark.extend(landmark_list)
        
        mp_drawing.draw_landmarks(
            display_frame,
            adjusted_pose,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
        )
    
    # Draw LIVE pose landmarks on the live frame (in GREEN)
    if live_results.pose_landmarks:
        mp_drawing.draw_landmarks(
            display_frame,
            live_results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2)
        )
    
    # Calculate and display accuracy score
    if saved_results.pose_landmarks and live_results.pose_landmarks:
        # Create adjusted landmarks for comparison
        landmark_list = []
        for landmark in saved_results.pose_landmarks.landmark:
            adjusted_landmark = type(landmark)()
            adjusted_landmark.x = (landmark.x - 0.5) * scale + 0.5 + offset_x
            adjusted_landmark.y = (landmark.y - 0.5) * scale + 0.5 + offset_y
            adjusted_landmark.z = landmark.z * scale
            adjusted_landmark.visibility = landmark.visibility
            landmark_list.append(adjusted_landmark)
        
        adjusted_pose = type(saved_results.pose_landmarks)()
        adjusted_pose.landmark.extend(landmark_list)
        
        # Calculate similarity
        accuracy = calculate_pose_similarity(adjusted_pose, live_results.pose_landmarks)
        
        # Display accuracy score with color coding
        if accuracy >= 80:
            color = (0, 255, 0)  # Green for good match
        elif accuracy >= 60:
            color = (0, 255, 255)  # Yellow for moderate match
        else:
            color = (0, 0, 255)  # Red for poor match
        
        cv2.putText(display_frame, f"Match: {accuracy:.1f}%", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3)
    
    # Display the live feed with overlays
    cv2.imshow('Live Feed - Comparing Poses (Press Q to Quit)', display_frame)
    
    # Wait for key press (1ms delay)
    key = cv2.waitKey(1) & 0xFF
    
    # Arrow keys for movement
    if key == 82 or key == 0:  # Up arrow
        offset_y -= move_step
    elif key == 84 or key == 1:  # Down arrow
        offset_y += move_step
    elif key == 81 or key == 2:  # Left arrow
        offset_x -= move_step
    elif key == 83 or key == 3:  # Right arrow
        offset_x += move_step
    
    # Scale controls
    elif key == ord('+') or key == ord('='):
        scale += scale_step
    elif key == ord('-') or key == ord('_'):
        scale = max(0.1, scale - scale_step)  # Prevent scale from going too small
    
    # Reset
    elif key == ord('r'):
        offset_x = 0.0
        offset_y = 0.0
        scale = 1.0
        print("Reset position and scale")
    
    # Press 'q' to quit
    elif key == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
pose.close()
print("Pose comparison closed")