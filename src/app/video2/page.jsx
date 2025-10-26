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

        {/* Hidden canvas for frame capture */}
        <canvas ref={canvasRef} className="hidden" />

        {/* Info */}
        <div className="mt-6 bg-blue-900/30 border border-blue-500/50 rounded-lg p-4">
          <p className="text-blue-200 text-sm">
            <strong>ℹ️ How it works:</strong> Your camera feed is captured in the browser, 
            frames are sent to the Python backend for OpenCV processing, and the processed 
            results are displayed in real-time using WebSockets.
          </p>
        </div>
      </div>
    </div>
  );
}
