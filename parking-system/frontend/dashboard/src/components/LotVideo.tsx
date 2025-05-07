import React from "react";

const LotVideo: React.FC = () => {
  return (
    <div>
      <h2>Lot Footage</h2>
      <video width="640" height="480" controls>
        <source src="http://127.0.0.1:5000//video" type="video/mp4" />
        Your browser does not support the video tag.
      </video>
    </div>
  );
};

export default LotVideo;
