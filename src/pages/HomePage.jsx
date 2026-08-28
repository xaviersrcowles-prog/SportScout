import { useCallback, useMemo, useRef, useState } from "react";
import SearchBar from "../components/SearchBar.jsx";
import FilterPanel from "../components/FilterPanel.jsx";
import FacilityList from "../components/FacilityList.jsx";
import FacilityDetails from "../components/FacilityDetails.jsx";
import MapFrame from "../components/MapFrame.jsx";
import { useSearch } from "../hooks/useSearch.js";
import { useSportsList } from "../hooks/useFacilities.js";

export default function HomePage() {
  const { results, status, error, center, runSearch } = useSearch();
  const sports = useSportsList();
  const mapRef = useRef(null);

  const [filters, setFilters] = useState({ sport: "", access: "", radius: 5, sort: "" });
  const [locationLabel, setLocationLabel] = useState("");
  const [selectedId, setSelectedId] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const selectedFacility = useMemo(
    () => results.find((r) => r.id === selectedId) || null,
    [results, selectedId]
  );

  const doSearch = useCallback(
    (location, nextFilters) => {
      const effective = nextFilters || filters;
      runSearch({
        lat: location.lat,
        lon: location.lon,
        radius: effective.radius,
        sport: effective.sport || undefined,
        access: effective.access || undefined,
        sort: effective.sort || undefined,
      });
      if (location.label) setLocationLabel(location.label);
    },
    [filters, runSearch]
  );

  function handleSearch(location) {
    doSearch(location);
  }

  function handleFilterChange(nextFilters) {
    setFilters(nextFilters);
    if (center) doSearch(center, nextFilters);
  }

  function handleSelectFromList(facilityId) {
    setSelectedId(facilityId);
    setDrawerOpen(true);
    mapRef.current?.selectMarker(facilityId);
  }

  function handleMarkerSelected(facilityId) {
    setSelectedId(facilityId);
    setDrawerOpen(true);
  }

  return (
    <div className="app-layout">
      <header className="app-header">
        <h1>SportScout</h1>
        <p className="tagline">Find sporting fields, courts and facilities near you.</p>
        <SearchBar onSearch={handleSearch} disabled={status === "loading"} />
        {locationLabel && <p className="location-label">Showing results near {locationLabel}</p>}
        <FilterPanel filters={filters} onChange={handleFilterChange} sports={sports} />
      </header>

      <main className="app-main">
        <section className="results-panel" aria-label="Search results">
          <FacilityList
            results={results}
            status={status}
            error={error}
            selectedId={selectedId}
            onSelect={handleSelectFromList}
          />
        </section>

        <section className="map-panel" aria-label="Map">
          <MapFrame ref={mapRef} results={results} onMarkerSelected={handleMarkerSelected} />
        </section>

        {drawerOpen && selectedFacility && (
          <FacilityDetails facility={selectedFacility} onClose={() => setDrawerOpen(false)} />
        )}
      </main>
    </div>
  );
}
