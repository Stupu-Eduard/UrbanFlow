import { useState, useEffect } from 'react';
import Map, { Source, Layer, Marker } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import './App.css';

// Mock data for demo
const MOCK_STREETS = [
  {
    id: 'street_1',
    name: 'Main Intersection - North',
    congestion: 0.44,
    level: 'medium' as const,
    coordinates: [[-73.98, 40.75], [-73.97, 40.76]],
  },
  {
    id: 'street_2',
    name: 'Downtown Avenue',
    congestion: 0.72,
    level: 'high' as const,
    coordinates: [[-73.97, 40.75], [-73.96, 40.76]],
  },
];

const MOCK_PARKING = [
  {
    id: 'zone_A',
    name: 'Central Parking Lot',
    latitude: 40.7589,
    longitude: -73.9762,
    free_spots: 5,
    total_spots: 10,
    occupancy_rate: 0.5,
  },
  {
    id: 'zone_B',
    name: 'North Parking Area',
    latitude: 40.7609,
    longitude: -73.9762,
    free_spots: 2,
    total_spots: 8,
    occupancy_rate: 0.75,
  },
];

const MAPBOX_TOKEN = 'pk.eyJ1IjoibmVndXJhdGVvZG9yciIsImEiOiJjbWgzaTJkcTAxNXkyZDNzYjlzbjg1andvIn0.J5GHR2HYPA3GxYuoS_xclA';

function App() {
  const [viewState, setViewState] = useState({
    longitude: -73.9762,
    latitude: 40.7589,
    zoom: 14,
  });
  const [activeView, setActiveView] = useState<'traffic' | 'parking'>('traffic');
  const [selectedParking, setSelectedParking] = useState<typeof MOCK_PARKING[0] | null>(null);

  const getCongestionColor = (level: string) => {
    switch (level) {
      case 'low': return '#10b981';
      case 'medium': return '#f59e0b';
      case 'high': return '#f97316';
      case 'critical': return '#ef4444';
      default: return '#3b82f6';
    }
  };

  const getParkingColor = (occupancy: number) => {
    if (occupancy < 0.5) return '#10b981';
    if (occupancy < 0.8) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="app">
      {/* Map */}
      <Map
        {...viewState}
        onMove={(evt) => setViewState(evt.viewState)}
        mapStyle="mapbox://styles/mapbox/dark-v11"
        mapboxAccessToken={MAPBOX_TOKEN}
        style={{ width: '100%', height: '100vh' }}
      >
        {/* Traffic Heat Map */}
        {MOCK_STREETS.map((street) => {
          const lineString = {
            type: 'Feature' as const,
            geometry: {
              type: 'LineString' as const,
              coordinates: street.coordinates,
            },
          };

          return (
            <Source key={street.id} type="geojson" data={lineString}>
              <Layer
                type="line"
                paint={{
                  'line-color': getCongestionColor(street.level),
                  'line-width': 8,
                  'line-opacity': 0.8,
                }}
              />
            </Source>
          );
        })}

        {/* Parking Markers */}
        {MOCK_PARKING.map((zone) => (
          <Marker
            key={zone.id}
            longitude={zone.longitude}
            latitude={zone.latitude}
            onClick={() => setSelectedParking(zone)}
          >
            <div
              className="parking-marker"
              style={{ borderColor: getParkingColor(zone.occupancy_rate) }}
            >
              <span className="parking-icon">🅿️</span>
              <span className="parking-badge">{zone.free_spots}</span>
            </div>
          </Marker>
        ))}
      </Map>

      {/* Header */}
      <div className="header">
        <h1>🚗 UrbanFlowAI</h1>
        <div className="header-subtitle">Real-Time Traffic & Parking Intelligence</div>
      </div>

      {/* View Toggle */}
      <button
        className="view-toggle"
        onClick={() => setActiveView(activeView === 'traffic' ? 'parking' : 'traffic')}
      >
        {activeView === 'traffic' ? '🅿️ Parking' : '📊 Traffic'}
      </button>

      {/* Bottom Panel */}
      <div className="bottom-panel">
        {activeView === 'traffic' ? (
          <div className="traffic-view">
            <h2>📊 Traffic Status</h2>
            <div className="congestion-bar">
              <div className="congestion-fill" style={{ width: '44%', backgroundColor: '#f59e0b' }} />
            </div>
            <div className="stat-row">
              <span className="stat-value">44%</span>
              <span className="stat-label">Average Congestion</span>
            </div>
            <div className="stats-grid">
              <div className="stat">
                <span className="stat-number">7</span>
                <span className="stat-text">parking spots free</span>
              </div>
              <div className="stat">
                <span className="stat-number">2</span>
                <span className="stat-text">streets monitored</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="parking-view">
            <h2>🅿️ Nearby Parking ({MOCK_PARKING.length})</h2>
            <div className="parking-list">
              {MOCK_PARKING.map((zone) => (
                <div key={zone.id} className="parking-card" onClick={() => setSelectedParking(zone)}>
                  <div className="parking-card-header">
                    <span className="parking-card-icon">🅿️</span>
                    <div className="parking-card-info">
                      <h3>{zone.name}</h3>
                      <p className="parking-card-id">{zone.id}</p>
                    </div>
                    <div
                      className="parking-card-badge"
                      style={{ backgroundColor: getParkingColor(zone.occupancy_rate) }}
                    >
                      {Math.round(zone.occupancy_rate * 100)}%
                    </div>
                  </div>
                  <div className="parking-card-stats">
                    <span className="parking-spots">
                      <strong>{zone.free_spots}</strong> of {zone.total_spots} spots free
                    </span>
                  </div>
                  <button className="navigate-btn">Navigate →</button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Parking Detail Modal */}
      {selectedParking && (
        <div className="modal-overlay" onClick={() => setSelectedParking(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <button className="close-btn" onClick={() => setSelectedParking(null)}>✕</button>
            <h2>🅿️ {selectedParking.name}</h2>
            <div className="modal-occupancy">
              <div className="occupancy-bar">
                <div
                  className="occupancy-fill"
                  style={{
                    width: `${selectedParking.occupancy_rate * 100}%`,
                    backgroundColor: getParkingColor(selectedParking.occupancy_rate),
                  }}
                />
              </div>
              <span className="occupancy-percent">{Math.round(selectedParking.occupancy_rate * 100)}%</span>
            </div>
            <div className="modal-stats">
              <div className="modal-stat">
                <span className="modal-stat-value" style={{ color: getParkingColor(selectedParking.occupancy_rate) }}>
                  {selectedParking.free_spots}
                </span>
                <span className="modal-stat-label">Available</span>
              </div>
              <div className="modal-stat">
                <span className="modal-stat-value">{selectedParking.total_spots - selectedParking.free_spots}</span>
                <span className="modal-stat-label">Occupied</span>
              </div>
              <div className="modal-stat">
                <span className="modal-stat-value">{selectedParking.total_spots}</span>
                <span className="modal-stat-label">Total</span>
              </div>
            </div>
            <button className="modal-navigate-btn">Start Navigation →</button>
          </div>
        </div>
      )}

      {/* Status Indicator */}
      <div className="status-indicator">
        <span className="status-dot"></span>
        Live Data • Updated 2s ago
      </div>
    </div>
  );
}

export default App;
