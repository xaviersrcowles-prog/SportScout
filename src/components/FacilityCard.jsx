import AccessBadge from "./AccessBadge.jsx";
import ConditionBadge from "./ConditionBadge.jsx";

export default function FacilityCard({ facility, selected, onSelect }) {
  return (
    <button
      type="button"
      className={`facility-card${selected ? " selected" : ""}`}
      onClick={() => onSelect(facility.id)}
      aria-pressed={selected}
    >
      <div className="facility-card-header">
        <h3>{facility.name}</h3>
        {typeof facility.distance_miles === "number" && (
          <span className="distance">{facility.distance_miles} mi</span>
        )}
      </div>

      <p className="facility-sports">
        {(facility.sport_types || []).join(", ") || facility.facility_type || "Facility"}
      </p>

      <div className="facility-badges">
        <AccessBadge access={facility.access} />
        <ConditionBadge condition={facility.condition} />
      </div>

      <p className="facility-hours">
        {facility.hours?.display ? facility.hours.display : "Hours unknown"}
      </p>
    </button>
  );
}
