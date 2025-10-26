'use client'
import { useRef, useState, useEffect } from 'react';

export default function VideoProcessor() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [processedImage, setProcessedImage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [fps, setFps] = useState(0);

  useEffect(() => {
    startCamera();
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 }
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error('Error accessing camera:', err);
    }
  };

  const captureAndSendFrame = async () => {
    if (!videoRef.current || !canvasRef.current || isProcessing) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    if (!context) return;

    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw current video frame to canvas
    context.drawImage(video, 0, 0);

    // Convert canvas to base64
    const imageData = canvas.toDataURL('image/jpeg', 0.8);

    setIsProcessing(true);
    const startTime = performance.now();

    try {
      const response = await fetch('http://134.199.133.46:5000/process-frame', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image: imageData }),
      });

      const data = await response.json();
      
      if (data.success) {
        setProcessedImage(data.processed_image);
        const endTime = performance.now();
        const processingTime = endTime - startTime;
        setFps(Math.round(1000 / processingTime));
      }
    } catch (error) {
      console.error('Error processing frame:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  // Process frames continuously
  useEffect(() => {
    const interval = setInterval(() => {
      captureAndSendFrame();
    }, 100); // Send frame every 100ms (10 FPS)

    return () => clearInterval(interval);
  }, [isProcessing]);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Video Frame Processor</h1>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <h2 className="text-lg font-semibold mb-2">Original Feed</h2>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            className="w-full border-2 border-gray-300 rounded"
          />
        </div>
        
        <div>
          <h2 className="text-lg font-semibold mb-2">Processed Feed (FPS: {fps})</h2>
          {processedImage ? (
            <img
              src={processedImage}
              alt="Processed"
              className="w-full border-2 border-gray-300 rounded"
            />
          ) : (
            <div className="w-full aspect-video bg-gray-200 flex items-center justify-center rounded">
              Waiting for processed frames...
            </div>
          )}
        </div>
      </div>

      <canvas ref={canvasRef} className="hidden" />
      
      <div className="mt-4">
        <p className="text-sm text-gray-600">
          {isProcessing ? 'Processing...' : 'Ready'}
        </p>
      </div>
    </div>
  );
}
