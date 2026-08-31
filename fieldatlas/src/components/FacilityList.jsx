import FacilityCard from "./FacilityCard.jsx";
import LoadingState from "./LoadingState.jsx";

export default function FacilityList({ results, status, error, selectedId, onSelect }) {
  if (status === "loading") {
    return <LoadingState label="Searching nearby facilities…" />;
  }

  if (status === "error") {
    return (
      <div className="empty-state error" role="alert">
        <p>{error || "Something went wrong."}</p>
      </div>
    );
  }

  if (status === "idle") {
    return (
      <div className="empty-state">
        <p>Search a city, address or ZIP code to find nearby sporting facilities.</p>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="empty-state">
        <p>No facilities found in this area. Try a larger radius or different filters.</p>
      </div>
    );
  }

  return (
    <ul className="facility-list" aria-label="Nearby facilities">
      {results.map((facility) => (
        <li key={facility.id}>
          <FacilityCard
            facility={facility}
            selected={facility.id === selectedId}
            onSelect={onSelect}
          />
        </li>
      ))}
    </ul>
  );
}
