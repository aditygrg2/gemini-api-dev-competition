// src/components/GifPlayer.js
import React, { useState } from 'react';

const GifPlayer = ({ staticImage, animatedGif, label }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [gifSrc, setGifSrc] = useState(staticImage); // Initially set the source to the static image

  const handleToggleGif = () => {
    if (isPlaying) {
      setGifSrc(staticImage); // Revert back to the static image
    } else {
      setGifSrc(animatedGif); // Start playing the animated GIF
    }
    setIsPlaying(!isPlaying); // Toggle the isPlaying state
  };

  return (
    <div className="flex flex-col items-center">
      <div className="mb-4">
        <img
          src={gifSrc}
          alt="GIF"
          className="w-64 h-64 mb-4"
        />
      </div>
      <button
        onClick={handleToggleGif}
        className="px-4 py-2 bg-blue-500 text-white font-semibold rounded"
      >
        {isPlaying ? 'Pause' : 'Play'} {label}
      </button>
    </div>
  );
}

export default GifPlayer;
