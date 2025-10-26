from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import cv2
import numpy as np
import base64
import threading
import queue
import time
import os
import mediapipe as mp
import mysql.connector

import posefunctions

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global queue and state
frame_queue = queue.Queue(maxsize=2)
processing_active = True
client_sid = None


# Execute query
# cursor.execute("SELECT * FROM exercises")

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Get module directory and load saved pose
module_path = os.path.abspath(__file__)
module_directory = os.path.dirname(module_path)


def get_saved_pose(file_name):
    saved_pose_path = os.path.join(module_directory, 'std_poses', file_name)

    # Load the saved pose image and get landmarks
    saved_results = None
    if os.path.exists(saved_pose_path):
        saved_image = cv2.imread(saved_pose_path)
        if saved_image is not None:
            saved_rgb = cv2.cvtColor(saved_image, cv2.COLOR_BGR2RGB)
            saved_results = pose.process(saved_rgb)
            if saved_results.pose_landmarks:
                pass
                # print("✓ Saved pose loaded successfully!")
            else:
                print("⚠️  Warning: No pose detected in saved image")
        else:
            print(f"⚠️  Warning: Could not load saved pose from {saved_pose_path}")
    else:
        print(f"⚠️  Warning: Saved pose file not found at {saved_pose_path}")
    
    return saved_results


def continuous_processing_loop():
    """
    Main processing loop that runs continuously.
    Waits for frames from the queue and processes them with MediaPipe.
    """

    # Offset and scale for saved pose overlay
    offset_x = 0.0
    offset_y = 0.0
    scale = 1.0

    x_offsets = np.array([])
    y_offsets = np.array([])
    scales = np.array([])

    posefile = 't_pose.jpg'
    saved_results = get_saved_pose('t_pose.jpg')

    global processing_active, client_sid
    
    print("🔄 Starting continuous pose processing loop...")
    num_frames = -1
    while processing_active:
        try:
            # print(scale)
            # initialize database
            if num_frames % 5 == 0 or num_frames == -1:
                connection = mysql.connector.connect(
                    host='localhost',      # or your server IP
                    user='sql',
                    password='knighthacks',
                    database='yogavision',
                    port=3306        
                     # default MariaDB port
                )
                # num_frames = 0s

            cursor = connection.cursor(dictionary=True, buffered=True)
            cursor.execute("SELECT * FROM exercises WHERE status IN (1, 3)")
            table_rows = cursor.fetchall()
            if len(table_rows) >= 1:
                # print(table_rows)
                exercise_id = table_rows[0]['id']
                exercise = table_rows[0]['exercise']
                category = table_rows[0]['category']
                status = table_rows[0]['status']
                # print(status)
                if len(table_rows) > 1:
                    print("More than 1 exercise of status 1")
            cursor.close()

            posefile = f'{exercise}_pose.jpg'

            # Wait for a frame from the queue
            frame_data = frame_queue.get(timeout=1.0)
            
            if frame_data is None:
                continue
            
            # Decode the frame
            image_data = frame_data['image'].split(',')[1]
            img_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                print("⚠️ Failed to decode image")
                continue
            
            

            # ====================================
            # MEDIAPIPE POSE PROCESSING
            # ====================================
            
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Process live frame with MediaPipe
            live_results = pose.process(rgb_frame)
            
            # Create display frame
            display_frame = img.copy()
            
            # calibration
            if status == 1:
                saved_results = get_saved_pose(posefile)
            
            # Draw SAVED pose landmarks (in RED) with offset and scale
            if saved_results and saved_results.pose_landmarks:
                # Create adjusted landmarks with offset and scale
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
                
                # Draw saved pose in RED
                mp_drawing.draw_landmarks(
                    display_frame,
                    adjusted_pose,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
                )
            
            # Draw LIVE pose landmarks (in GREEN)
            if live_results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    display_frame,
                    live_results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2)
                )
            
            # Calculate accuracy score
            accuracy = 0.0
            if saved_results and saved_results.pose_landmarks and live_results.pose_landmarks:
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
                accuracy = posefunctions.calculate_pose_similarity_wo_face(adjusted_pose, live_results.pose_landmarks)
                #if status == 1 and accuracy < 90 and live_results.pose_landmarks:
                   # temp_x, temp_y, temp_scale = posefunctions.calculate_alignment(adjusted_pose, live_results.pose_landmarks)
                    
                   # x_offsets = np.append(x_offsets, temp_x)
                   # y_offsets = np.append(y_offsets, temp_y)
                   # scales = np.append(scales, temp_scale)

                   # if num_frames % 10 == 0:
                   #     offset_x = np.mean(x_offsets)
                   #     offset_y = np.mean(y_offsets)
                   #     scale = np.mean(scales)

                    #    x_offsets = np.array([])
                     #   y_offsets = np.array([])
                      #  scales = np.array([])
                if accuracy >= 80 and status == 2:
                    cursor.execute(
                        "UPDATE exercises SET status = %s WHERE id = %s",
                        (str(2), exercise_id)
                    )
                    connection.commit()
                    

                # Display accuracy with color coding
                if accuracy >= 80:
                    color = (0, 255, 0)  # Green
                elif accuracy >= 60:
                    color = (0, 255, 255)  # Yellow
                else:
                    color = (0, 0, 255)  # Red
                
                cv2.putText(display_frame, f"Match: {accuracy:.1f}%", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3)
            
            num_frames += 1
            if num_frames > 99:
                num_frames = 0
            # ====================================
            # END PROCESSING
            # ====================================
            
            # Encode processed frame
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
            _, buffer = cv2.imencode('.jpg', img=display_frame, params=encode_param)
            processed_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Send back to client with accuracy score
            if client_sid:
                socketio.emit('processed_frame', {
                    'image': f'data:image/jpeg;base64,{processed_base64}',
                    'accuracy': accuracy
                }, room=client_sid)
            
            frame_queue.task_done()
            
        except queue.Empty:
            continue
        except Exception as e:
            print(f"❌ Error in processing loop: {str(e)}")
            import traceback
            traceback.print_exc()
            time.sleep(0.1)
    
    print("🛑 Processing loop stopped")

@socketio.on('frame')
def handle_frame(data):
    """Receive frames from frontend and add to queue"""
    global frame_queue
    
    try:
        if frame_queue.full():
            try:
                frame_queue.get_nowait()
            except queue.Empty:
                pass
        
        frame_queue.put(data, block=False)
        
    except queue.Full:
        pass
    except Exception as e:
        print(f"❌ Error queuing frame: {str(e)}")

@socketio.on('adjust_pose')
def handle_adjust_pose(data):
    """Handle pose adjustment controls from frontend"""
    global offset_x, offset_y, scale
    
    action = data.get('action')
    
    if action == 'move_up':
        offset_y -= 0.01
    elif action == 'move_down':
        offset_y += 0.01
    elif action == 'move_left':
        offset_x -= 0.01
    elif action == 'move_right':
        offset_x += 0.01
    elif action == 'scale_up':
        scale += 0.05
    elif action == 'scale_down':
        scale = max(0.1, scale - 0.05)
    elif action == 'reset':
        offset_x = 0.0
        offset_y = 0.0
        scale = 1.0
    
    emit('pose_adjusted', {'offset_x': offset_x, 'offset_y': offset_y, 'scale': scale})

@socketio.on('connect')
def handle_connect():
    global client_sid
    from flask import request
    client_sid = request.sid
    print(f'✅ Client connected: {client_sid}')
    emit('status', {'message': 'Connected to pose processing server'})

@socketio.on('disconnect')
def handle_disconnect():
    global client_sid
    from flask import request
    print(f'❌ Client disconnected: {request.sid}')
    if client_sid == request.sid:
        client_sid = None
    
    while not frame_queue.empty():
        try:
            frame_queue.get_nowait()
        except queue.Empty:
            break

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Starting Flask-SocketIO Pose Comparison Server...")
    print("=" * 50)
    
    # Start the continuous processing thread
    processing_thread = threading.Thread(
        target=continuous_processing_loop, 
        daemon=True,
        name="PoseProcessingThread"
    )
    processing_thread.start()
    print("✓ Processing thread started")
    
    # Start the Flask-SocketIO server on HTTP (no SSL)
    print("✓ Listening on http://0.0.0.0:5000")
    print("✓ Waiting for frames from frontend...")
    print("⚠️  Note: Camera access requires HTTPS in production")
    print("=" * 50)
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
    finally:
        processing_active = False
        pose.close()
        print("🛑 Shutting down...")
