// src/App.js
import React, { useState, useEffect, useRef } from 'react';
import GifPlayer from './components/GifPlayer';
import gifPlaceholder from './frame1.png'; // Replace with the path to your static placeholder image
import customerGifPlaceholder from './headphone.jpg'
import gifAnimatedCustomer from './customer.gif'; // Replace with the path to your customer animated GIF
import gifAnimatedParallel from './customer_headphone.gif'; // Replace with the path to your parallel animated GIF
import io from 'socket.io-client';
import { ReactMic } from 'react-mic'

const socket = io('http://localhost:8000'); // Update the port as per your backend

function App() {
  const [record, setRecord] = useState(false);
  const [receivedAudio, setReceivedAudio] = useState(null);
  const [recordedUrl, setRecordedUrl] = useState('');
  const mediaStream = useRef(null);
  const mediaRecorder = useRef(null);
  const chunks = useRef([]);

  const startRecording = async () => {
    setRecord(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      mediaStream.current = stream;
      
      mediaRecorder.current = new MediaRecorder(stream);
      
      mediaRecorder.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.current.push(e.data);
        }
      };
      
      mediaRecorder.current.onstop = () => {
        const recordedBlob = new Blob(chunks.current, { type: 'audio/webm' });
        const url = URL.createObjectURL(recordedBlob);
        setRecordedUrl(url);
        chunks.current = [];

        const reader = new FileReader();
        reader.onload = () => {
          const base64data = reader.result.split(',')[1];
          socket.emit('send_audio', base64data);
        };
        reader.readAsDataURL(recordedBlob);
      };
      
      mediaRecorder.current.start();

    } catch (error) {
      console.error('Error accessing microphone:', error);
    }
  };

  const stopRecording = () => {
    setRecord(false);

    if (mediaRecorder.current && mediaRecorder.current.state === 'recording') {
      mediaRecorder.current.stop();
    }

    if (mediaStream.current) {
      mediaStream.current.getTracks().forEach((track) => {
        track.stop();
      });
    }
  };

  useEffect(() => {
    socket.on('receive_audio', (data) => {
      console.log("We have some data here");
      const audioBlob = new Blob([data], { type: 'audio/wav' });
      setReceivedAudio(URL.createObjectURL(audioBlob));
    });
  }, []);

  return (
    <div className="flex flex-col justify-center items-center min-h-screen bg-gradient-to-r from-yellow-400 via-yellow-300 to-yellow-500">
      <div className="flex justify-around items-center w-full max-w-screen-lg">
        <GifPlayer
          staticImage={gifPlaceholder}
          animatedGif={gifAnimatedCustomer}
          label="Customer"
        />

        <GifPlayer
          staticImage={customerGifPlaceholder}
          animatedGif={gifAnimatedParallel}
          label="Agent"
        />
      </div>
      <div>
        <ReactMic
          record={record}
          onStop={stopRecording}
          strokeColor="#000000"
          backgroundColor="#FF4081"
        />
      </div>
      <div className='flex flex-row justify-around w-1/2 mt-10'>
        <button
          onClick={startRecording}
          className="px-4 py-2 bg-blue-500 text-white font-semibold rounded"
        >
          Start
        </button>
        <button
          onClick={stopRecording}
          className="px-4 py-2 bg-blue-500 text-white font-semibold rounded"
        >
          Stop
        </button>
        {receivedAudio && (
          <audio controls>
            <source src={receivedAudio} type="audio/wav" />
            Your browser does not support the audio element.
          </audio>
        )}
      </div>
    </div>
  );
}

export default App;