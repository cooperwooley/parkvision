interface ParkingSpace {
  id: number;
  x: number;
  y: number;
  width: number;
  height: number;
  status: 'empty' | 'occupied';
}

export default function SpatialParkingLotMap({ lotStatus }: { lotStatus: ParkingSpace[] | null }) {
  if (!lotStatus || !Array.isArray(lotStatus)) return <div>No parking data available</div>;

  const SCALE = 0.8;
  const VERTICAL_GAP_ADJUSTMENT = 0.91;
  const OPACITY = 0.7;

  const maxX = Math.max(...lotStatus.map(spot => spot.x + spot.width)) + 20;
  const maxY = Math.max(...lotStatus.map(spot => spot.y + spot.height)) + 20;

  return (
    <div
      className="parking-lot-wrapper"
      style={{
        position: 'relative',
        width: `${maxX}px`,
        height: `${maxY}px`,
        margin: '0 auto',
      }}
    >
      {/* Video Background */}
      <video
        src="/lot_footage.mp4"
        autoPlay
        loop
        muted
        playsInline
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          zIndex: 0
        }}
      />
      
      {/* Parking Spots */}
      {lotStatus.map((spot) => {

        // Adjust the vertical spacing by modifying y position
        const adjustedTop = spot.y * VERTICAL_GAP_ADJUSTMENT;  // Reduce gap vertically

        // Define different shifts for left and top based on spot.id
        const leftShiftAmount = spot.id >= 19 ? 37 : 0; // Shift left by 20px if id >= 19
        const topShiftAmount = spot.id >= 19 ? 2 : 0;  // Shift up by 15px if id >= 19

        return (
          <div
            key={spot.id}
            className={`space ${spot.status === 'occupied' ? 'occupied' : 'available'}`}
            style={{
              position: 'absolute',
              left: `${spot.x + 25 - leftShiftAmount}px`, // Apply left shift if id >= 19
              top: `${adjustedTop + 5 - topShiftAmount}px`,  // Apply top shift if id >= 19
              width: `${spot.width * SCALE}px`,
              height: `${spot.height * SCALE}px`,
              border: '2px solid #333',
              backgroundColor: spot.status === 'occupied' ? '#ff6b6b' : '#4cd137',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              fontSize: '14px',
              color: spot.status === 'occupied' ? 'white' : 'black',
              borderRadius: '4px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              transition: 'background-color 0.3s ease',
              zIndex: 1,
              opacity: OPACITY
            }}
          >
            {spot.id}
            <span style={{ fontSize: '12px' }}>
              {spot.status === 'occupied' ? 'Occupied' : 'Available'}
            </span>
          </div>
        );
      })}
    </div>
  );
}
