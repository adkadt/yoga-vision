from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import cv2
import numpy as np
import base64
import threading
import queue
import time

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global queue and state
frame_queue = queue.Queue(maxsize=2)  # Limit queue size to avoid memory issues
processing_active = True
client_sid = None

def continuous_processing_loop():
    """
    Main processing loop that runs continuously.
    Waits for frames from the queue and processes them.
    """
    global processing_active, client_sid
    
    print("🔄 Starting continuous processing loop...")
    
    while processing_active:
        try:
            # Wait for a frame from the queue (blocks until frame arrives)
            # Timeout after 1 second to check if we should still be running
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
            # YOUR OPENCV PROCESSING HERE
            # ====================================
            # Example: Convert to grayscale
            processed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # You can add any processing here:
            # - Pose detection
            # - Object detection
            # - Image filters
            # - etc.
            
            # Add processing time simulation (remove in production)
            # time.sleep(0.01)  # Simulate 10ms processing time
            
            # ====================================
            # END PROCESSING
            # ====================================
            
            # Encode processed frame
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 60]
            _, buffer = cv2.imencode('.jpg', processed, encode_param)
            processed_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Send back to the specific client
            if client_sid:
                socketio.emit('processed_frame', {
                    'image': f'data:image/jpeg;base64,{processed_base64}'
                }, room=client_sid)
            
            # Mark task as done
            frame_queue.task_done()
            
        except queue.Empty:
            # No frame received in timeout period, continue waiting
            continue
            
        except Exception as e:
            print(f"❌ Error in processing loop: {str(e)}")
            time.sleep(0.1)
    
    print("🛑 Processing loop stopped")

@socketio.on('frame')
def handle_frame(data):
    """
    Receive frames from frontend and add to queue for processing.
    Non-blocking - just queues the frame and returns immediately.
    """
    global frame_queue
    
    try:
        # If queue is full, remove oldest frame and add new one
        if frame_queue.full():
            try:
                frame_queue.get_nowait()  # Remove old frame
            except queue.Empty:
                pass
        
        # Add new frame to queue
        frame_queue.put(data, block=False)
        
    except queue.Full:
        # Queue is full, skip this frame
        pass
    except Exception as e:
        print(f"❌ Error queuing frame: {str(e)}")

@socketio.on('connect')
def handle_connect():
    global client_sid
    from flask import request
    client_sid = request.sid
    print(f'✅ Client connected: {client_sid}')
    emit('status', {'message': 'Connected to processing server'})

@socketio.on('disconnect')
def handle_disconnect():
    global client_sid
    from flask import request
    print(f'❌ Client disconnected: {request.sid}')
    if client_sid == request.sid:
        client_sid = None
    
    # Clear the queue when client disconnects
    while not frame_queue.empty():
        try:
            frame_queue.get_nowait()
        except queue.Empty:
            break

@socketio.on('ping')
def handle_ping():
    """Heartbeat to check connection"""
    emit('pong')

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Starting Flask-SocketIO server...")
    print("=" * 50)
    
    # Start the continuous processing thread
    processing_thread = threading.Thread(
        target=continuous_processing_loop, 
        daemon=True,
        name="ProcessingThread"
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
        print("🛑 Shutting down...")
