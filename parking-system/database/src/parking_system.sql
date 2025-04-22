CREATE TABLE parking_lots (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    total_spaces INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE parking_spots (
    id SERIAL PRIMARY KEY,
    parking_lot_id INTEGER REFERENCES parking_lots(id) ON DELETE CASCADE,
    spot_number VARCHAR(20) NOT NULL,
    -- Coordinates for the bouding box
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

CREATE TABLE spot_status (
    id SERIAL PRIMARY KEY,
    parking_spot_id INTEGER REFERENCES parking_spots(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('available', 'occupied')),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- For image recognition
    detection_method VARCHAR(50), -- 'background_subtraction', etc.
    image_path TEXT -- Optional: path to snapshot that triggered status change
);

-- If planning authenticated access
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE TABLE parking_analytics (
    id SERIAL PRIMARY KEY,
    parking_lot_id INTEGER REFERENCES parking_lots(id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_spaces INTEGER NOT NULL,
    occupied_spaces INTEGER NOT NULL,
    occupancy_rate FLOAT GENERATED ALWAYS AS (CASE WHEN total_spaces > 0 THEN occupied_spaces::FLOAT / total_spaces ELSE 0 END) STORED,
    -- Additional metrics
    peak_hour BOOLEAN DEFAULT FALSE
);

-- Indexes for frequently queuried columns
CREATE INDEX idx_spot_status_spot_id ON spot_status(parking_spot_id);
CREATE INDEX idx_spot_status_timestamp ON spot_status(detected_at);

-- Functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS %%
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for timestamp updates
CREATE TRIGGER update_parking_lots_modtime
BEFORE UPDATE ON parking_lots
FOR EACH ROW EXECUTE FUNCTION update_modified_column();