import { useState } from "react";

async function geocode(placeText) {
  const params = new URLSearchParams({
    q: placeText,
    format: "jsonv2",
    limit: "1",
    countrycodes: "us",
  });
  const response = await fetch(`https://nominatim.openstreetmap.org/search?${params.toString()}`, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) throw new Error("Location lookup failed.");
  const results = await response.json();
  if (!results.length) throw new Error("No location found for that search.");
  return { lat: parseFloat(results[0].lat), lon: parseFloat(results[0].lon), label: results[0].display_name };
}

export default function SearchBar({ onSearch, disabled }) {
  const [placeText, setPlaceText] = useState("");
  const [locating, setLocating] = useState(false);
  const [localError, setLocalError] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    setLocalError(null);

    if (!placeText.trim()) {
      setLocalError("Enter a city, address or ZIP code.");
      return;
    }

    try {
      setLocating(true);
      const location = await geocode(placeText.trim());
      onSearch({ lat: location.lat, lon: location.lon, label: location.label });
    } catch (err) {
      setLocalError(err.message || "Could not find that location.");
    } finally {
      setLocating(false);
    }
  }

  function handleUseMyLocation() {
    if (!navigator.geolocation) {
      setLocalError("Geolocation is not available in this browser.");
      return;
    }
    setLocalError(null);
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocating(false);
        onSearch({
          lat: position.coords.latitude,
          lon: position.coords.longitude,
          label: "Current location",
        });
      },
      () => {
        setLocating(false);
        setLocalError("Could not get your location.");
      },
      { enableHighAccuracy: false, timeout: 8000 }
    );
  }

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <label htmlFor="place-search" className="visually-hidden">
        Search by city, address or ZIP code
      </label>
      <input
        id="place-search"
        type="text"
        placeholder="City, address or ZIP code"
        value={placeText}
        onChange={(e) => setPlaceText(e.target.value)}
        disabled={disabled || locating}
      />
      <button type="submit" disabled={disabled || locating}>
        {locating ? "Searching…" : "Search"}
      </button>
      <button
        type="button"
        className="secondary"
        onClick={handleUseMyLocation}
        disabled={disabled || locating}
      >
        Use my location
      </button>
      {localError && (
        <p className="field-error" role="alert">
          {localError}
        </p>
      )}
    </form>
  );
}
