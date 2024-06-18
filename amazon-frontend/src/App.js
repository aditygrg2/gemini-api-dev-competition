import React, { useState, useEffect, useRef } from 'react';
import GifPlayer from './components/GifPlayer';
import gifPlaceholder from './frame1.png'; // Replace with the path to your static placeholder image
import customerGifPlaceholder from './headphone.jpg';
import gifAnimatedCustomer from './customer.gif'; // Replace with the path to your customer animated GIF
import gifAnimatedParallel from './customer_headphone.gif'; // Replace with the path to your parallel animated GIF
import io from 'socket.io-client';
import { ReactMic } from 'react-mic';
import amazon from './images.png'

const socket = io('http://localhost:8000'); // Update the port as per your backend

function App() {
  const [record, setRecord] = useState(false);
  const [receivedAudio, setReceivedAudio] = useState(null);
  const [recordedUrl, setRecordedUrl] = useState('');
  const [isCustomerGifPlaying, setIsCustomerGifPlaying] = useState(false);
  const [isAgentGifPlaying, setIsAgentGifPlaying] = useState(false);
  const mediaStream = useRef(null);
  const mediaRecorder = useRef(null);
  const inputRef = useRef();
  const chunks = useRef([]);
  const sourceRef = useRef();

  const startRecording = async () => {
    setRecord(true);
    setIsCustomerGifPlaying(true);
    setIsAgentGifPlaying(true);
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
          socket.emit('send_audio', {
            data: base64data,
            phone_number: inputRef.current.value
          });
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
    setIsCustomerGifPlaying(false);
    setIsAgentGifPlaying(false);

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
      sourceRef.current = URL.createObjectURL(audioBlob);
    });
  }, []);

  return (
    <div className="flex flex-col justify-between items-center min-h-screen bg-gradient-to-r from-gray-100 via-gray-200 to-gray-300 p-4">
      <header className="w-full flex justify-center items-center p-4 bg-gray-800 text-white mb-8 rounded-lg shadow-md">
        <div className="flex items-center space-x-4">
          <img src={amazon} alt="Amazon Logo" className="h-16 w-24" />
          <div className="h-16 border-l border-white"></div>
          <h1 className="text-2xl font-bold">Customer Service Interface</h1>
        </div>
      </header>
      <div className="flex justify-around items-center w-full max-w-screen-lg mb-8 flex-grow">
        <div className="flex flex-col items-center">
          <GifPlayer
            staticImage={gifPlaceholder}
            animatedGif={gifAnimatedCustomer}
            isPlaying={isCustomerGifPlaying}
            label=""
          />
          <div className="mt-4 px-4 py-2 bg-blue-500 text-white font-bold text-xl rounded-lg shadow-md">
            Customer
          </div>
        </div>

        <div className="flex flex-col items-center">
          <GifPlayer
            staticImage={customerGifPlaceholder}
            animatedGif={gifAnimatedParallel}
            isPlaying={isAgentGifPlaying}
            label=""
          />
          <div className="mt-4 px-4 py-2 bg-green-500 text-white font-bold text-xl rounded-lg shadow-md">
            Agent
          </div>
        </div>
      </div>
      <div className="mb-8">
        <ReactMic
          record={record}
          onStop={stopRecording}
          strokeColor="#000000"
          backgroundColor="#FF4081"
        />
      </div>
      <div className='flex flex-row justify-around w-full max-w-md mb-8'>
        <button
          onClick={startRecording}
          className="px-4 py-2 bg-blue-500 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md transition duration-300"
        >
          Start
        </button>
        <input
          ref={inputRef}
          type="number"
          placeholder="Enter your phone number"
          className="px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-300"
        />
        <button
          onClick={stopRecording}
          className="px-4 py-2 bg-blue-500 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md transition duration-300"
        >
          Stop
        </button>
      </div>
      {receivedAudio && (
        <div className="mt-8">
          <audio controls className="w-full max-w-md">
            <source src={receivedAudio} type="audio/wav" />
            Your browser does not support the audio element.
          </audio>
        </div>
      )}
      <footer className="w-full text-center p-4 bg-gray-800 text-white mt-8 rounded-lg shadow-md">
        <p>&copy; 2024 Customer Service. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;
