import cv2
import mediapipe as mp
import time
from datetime import datetime
from picamera2 import Picamera2

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def save_pose_to_file(image, frame_number, filename="pose_image.jpg"):
    """Save the captured image to file."""
    # Save the image
    cv2.imwrite(filename, image)
    print(f"Image saved as {filename}")

def main():
    # Initialize Pi Camera with picamera2
    picam2 = Picamera2()
    
    # Configure camera with preview mode
    config = picam2.create_preview_configuration(
        main={"size": (640, 480), "format": "RGB888"}
    )
    picam2.configure(config)
    
    # Enable continuous autofocus if supported
    try:
        picam2.set_controls({"AfMode": 2})  # 2 = Continuous autofocus
        print("Continuous autofocus enabled")
    except Exception as e:
        print(f"Autofocus not available: {e}")
    
    picam2.start()
    time.sleep(2)  # Let camera warm up
    
    frame_number = 0
    save_interval = 30  # Save pose every 30 frames (adjust as needed)
    
    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:
        
        print("Press 'q' to quit")
        print("Press 's' to save current pose")
        print(f"Auto-saving every {save_interval} frames")
        
        while True:
            image = picam2.capture_array()
            
            # Convert RGB to BGR for OpenCV
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            
            # Process the image and detect poses
            results = pose.process(image_rgb)
            
            # Draw pose landmarks on the image
            image_rgb.flags.writeable = True
            image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
            
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
                
                # Auto-save at intervals
                if frame_number % save_interval == 0:
                    save_pose_to_file(image, frame_number)
                    print(f"Image saved at frame {frame_number}")
            
            # Display frame number
            cv2.putText(image, f"Frame: {frame_number}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow('MediaPipe Pose', image)
            
            key = cv2.waitKey(5) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                save_pose_to_file(image, frame_number)
                print(f"Manually saved image at frame {frame_number}")
            
            frame_number += 1
    
    picam2.stop()
    cv2.destroyAllWindows()
    print(f"Program ended. Total frames processed: {frame_number}")

if __name__ == "__main__":
    main()