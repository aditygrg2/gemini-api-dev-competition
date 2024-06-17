// src/App.js
import React from 'react';
import GifPlayer from './components/GifPlayer';
import gifPlaceholder from './frame1.png'; // Replace with the path to your static placeholder image
import customerGifPlaceholder from './headphone.jpg'
import gifAnimatedCustomer from './customer.gif'; // Replace with the path to your customer animated GIF
import gifAnimatedParallel from './customer_headphone.gif'; // Replace with the path to your parallel animated GIF

function App() {
  return (
    <div className="flex justify-center items-center min-h-screen bg-gradient-to-r from-yellow-400 via-yellow-300 to-yellow-500">
      <div className="flex justify-around items-center w-full max-w-screen-lg">
        {/* Customer GIF Section */}
        <GifPlayer
          staticImage={gifPlaceholder}
          animatedGif={gifAnimatedCustomer}
          label="Customer"
        />

        {/* Parallel GIF Section */}
        <GifPlayer
          staticImage={customerGifPlaceholder}
          animatedGif={gifAnimatedParallel}
          label="Parallel"
        />
      </div>
    </div>
  );
}

export default App;
