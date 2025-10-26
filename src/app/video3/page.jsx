'use client';

import { useRef, useState, useEffect } from 'react';
import { io } from 'socket.io-client';

export default function VideoProcessor() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const socketRef = useRef(null);
  const [processedImage, setProcessedImage] = useState('');
  const [fps, setFps] = useState(0);
  const [connected, setConnected] = useState(false);
  const [cameraReady, setCameraReady] = useState(false);
  const [poseOffset, setPoseOffset] = useState({ x: 0, y: 0, scale: 1.0 });
  const lastFrameTime = useRef(Date.now());
  const frameCount = useRef(0);

  useEffect(() => {
    startCamera();
    connectWebSocket();

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const connectWebSocket = () => {
    // Connect via HTTP to Flask backend
    socketRef.current = io('http://yogavision.abrandt.xyz:5000', {
      transports: ['websocket', 'polling']
    });
    
    socketRef.current.on('connect', () => {
      console.log('Connected to WebSocket server');
      setConnected(true);
    });

    socketRef.current.on('disconnect', () => {
      console.log('Disconnected from WebSocket server');
      setConnected(false);
    });
    
    socketRef.current.on('processed_frame', (data) => {
      setProcessedImage(data.image);
      
      // Calculate FPS
      frameCount.current++;
      const now = Date.now();
      
      if (frameCount.current % 5 === 0) {
        const timeDiff = now - lastFrameTime.current;
        setFps(Math.round(5000 / timeDiff));
        lastFrameTime.current = now;
      }
    });

    socketRef.current.on('pose_adjusted', (data) => {
      setPoseOffset({
        x: data.offset_x,
        y: data.offset_y,
        scale: data.scale
      });
      console.log('Pose adjusted:', data);
    });

    socketRef.current.on('status', (data) => {
      console.log('Status:', data.message);
    });

    socketRef.current.on('error', (data) => {
      console.error('Server error:', data.message);
    });
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { 
          width: 320, 
          height: 240,
          facingMode: 'user'
        }
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          setCameraReady(true);
        };
      }
    } catch (err) {
      console.error('Error accessing camera:', err);
      alert('Could not access camera. Please ensure HTTPS is enabled and camera permissions are granted.');
    }
  };

  const captureAndSendFrame = () => {
    if (!videoRef.current || !canvasRef.current || !socketRef.current || !connected || !cameraReady) {
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    if (!context || video.readyState !== video.HAVE_ENOUGH_DATA) {
      return;
    }

    // Set canvas to match video size
    canvas.width = 320;
    canvas.height = 240;
    
    // Draw current frame
    context.drawImage(video, 0, 0, 320, 240);

    // Convert to base64 with lower quality for speed
    const imageData = canvas.toDataURL('image/jpeg', 0.5);
    
    // Send via WebSocket
    socketRef.current.emit('frame', { image: imageData });
  };

  // Continuously send frames
  useEffect(() => {
    if (!cameraReady || !connected) return;

    const interval = setInterval(() => {
      captureAndSendFrame();
    }, 33); // ~30 FPS

    return () => clearInterval(interval);
  }, [cameraReady, connected]);

  const adjustPose = (action) => {
    if (socketRef.current && connected) {
      socketRef.current.emit('adjust_pose', { action });
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-2 text-white">
          Live Video Processing
        </h1>
        <p className="text-gray-400 mb-6">
          Camera feed from your device, processed on the server
        </p>
        
        {/* Status Bar */}
        <div className="bg-gray-800 rounded-lg p-4 mb-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-white font-medium">
                {connected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            <div className="text-gray-400">|</div>
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${cameraReady ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
              <span className="text-white font-medium">
                {cameraReady ? 'Camera Active' : 'Camera Loading...'}
              </span>
            </div>
            <div className="text-gray-400">|</div>
            <div className="text-white">
              <span className="font-semibold">{fps}</span> FPS
            </div>
          </div>
        </div>

        {/* Video Grid - but only showing processed output */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Original Feed - HIDDEN but still in DOM */}
          <div className="bg-gray-800 rounded-lg overflow-hidden" style={{ visibility: 'hidden', position: 'absolute' }}>
            <div className="bg-gray-700 px-4 py-2">
              <h2 className="text-lg font-semibold text-white">Your Camera</h2>
            </div>
            <div className="aspect-video bg-black">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-contain"
              />
            </div>
          </div>
          
          {/* Processed Feed - centered and full width */}
          <div className="bg-gray-800 rounded-lg overflow-hidden lg:col-span-2">
            <div className="bg-gray-700 px-4 py-2">
              <h2 className="text-lg font-semibold text-white">Processed Output</h2>
            </div>
            <div className="aspect-video bg-black flex items-center justify-center">
              {processedImage ? (
                <img
                  src={processedImage}
                  alt="Processed"
                  className="w-full h-full object-contain"
                />
              ) : (
                <div className="text-gray-500 text-center">
                  <div className="text-4xl mb-2">⚙️</div>
                  <p>Waiting for processed frames...</p>
                  {!connected && <p className="text-sm mt-2">Check server connection</p>}
                  {!cameraReady && connected && <p className="text-sm mt-2">Initializing camera...</p>}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Pose Adjustment Controls */}
        <div className="mt-6 bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Target Pose Controls</h2>
          <p className="text-gray-400 text-sm mb-4">
            Adjust the position and scale of the red target pose overlay
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Position Controls */}
            <div className="bg-gray-700 rounded-lg p-4">
              <h3 className="text-white font-medium mb-3">Position</h3>
              <div className="grid grid-cols-3 gap-2">
                <div></div>
                <button
                  onClick={() => adjustPose('move_up')}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition"
                  disabled={!connected}
                >
                  ↑
                </button>
                <div></div>
                <button
                  onClick={() => adjustPose('move_left')}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition"
                  disabled={!connected}
                >
                  ←
                </button>
                <div className="flex items-center justify-center text-gray-400 text-xs">
                  Move
                </div>
                <button
                  onClick={() => adjustPose('move_right')}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition"
                  disabled={!connected}
                >
                  →
                </button>
                <div></div>
                <button
                  onClick={() => adjustPose('move_down')}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition"
                  disabled={!connected}
                >
                  ↓
                </button>
                <div></div>
              </div>
              <div className="mt-3 text-xs text-gray-400 text-center">
                X: {poseOffset.x.toFixed(3)} | Y: {poseOffset.y.toFixed(3)}
              </div>
            </div>

            {/* Scale Controls */}
            <div className="bg-gray-700 rounded-lg p-4">
              <h3 className="text-white font-medium mb-3">Scale</h3>
              <div className="flex flex-col gap-3">
                <button
                  onClick={() => adjustPose('scale_up')}
                  className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded transition"
                  disabled={!connected}
                >
                  + Larger
                </button>
                <button
                  onClick={() => adjustPose('scale_down')}
                  className="bg-orange-600 hover:bg-orange-700 text-white font-bold py-3 px-4 rounded transition"
                  disabled={!connected}
                >
                  - Smaller
                </button>
              </div>
              <div className="mt-3 text-xs text-gray-400 text-center">
                Scale: {poseOffset.scale.toFixed(2)}x
              </div>
            </div>

            {/* Reset */}
            <div className="bg-gray-700 rounded-lg p-4 flex flex-col justify-center">
              <h3 className="text-white font-medium mb-3">Reset</h3>
              <button
                onClick={() => adjustPose('reset')}
                className="bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-4 rounded transition"
                disabled={!connected}
              >
                Reset to Default
              </button>
              <p className="mt-3 text-xs text-gray-400 text-center">
                Restores original position and scale
              </p>
            </div>
          </div>
        </div>

        {/* Hidden canvas for frame capture */}
        <canvas ref={canvasRef} className="hidden" />

        {/* Info */}
        <div className="mt-6 bg-blue-900/30 border border-blue-500/50 rounded-lg p-4">
          <p className="text-blue-200 text-sm">
            <strong>ℹ️ How it works:</strong> Your camera feed is captured in the browser, 
            frames are sent to the Python backend for OpenCV processing, and the processed 
            results are displayed in real-time using WebSockets. Use the controls above to 
            align the red target pose with your body for accurate tracking.
          </p>
        </div>
      </div>
    </div>
  );
}
