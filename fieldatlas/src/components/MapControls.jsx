export default function MapControls({ onZoomIn, onZoomOut, onRecenter }) {
  return (
    <div className="map-controls" role="group" aria-label="Map controls">
      <button type="button" onClick={onZoomIn} aria-label="Zoom in">
        +
      </button>
      <button type="button" onClick={onZoomOut} aria-label="Zoom out">
        −
      </button>
      <button type="button" onClick={onRecenter} aria-label="Fit results">
        ⤢
      </button>
    </div>
  );
}
