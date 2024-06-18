import React from 'react';

const GifPlayer = ({ staticImage, animatedGif, isPlaying, label }) => {
  const gifSrc = isPlaying ? animatedGif : staticImage;

  return (
    <div className="flex flex-col items-center">
      <div className="mb-4">
        <img
          src={gifSrc}
          alt={`${label} GIF`}
          className="w-64 h-64 mb-4"
        />
      </div>
      <div>{label}</div>
    </div>
  );
}

export default GifPlayer;
