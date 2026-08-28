const RADII = [1, 5, 10, 25];
const ACCESS_OPTIONS = [
  { value: "", label: "Any access" },
  { value: "public", label: "Public" },
  { value: "restricted", label: "Restricted" },
  { value: "members_only", label: "Members only" },
  { value: "private", label: "Private" },
];
const SORT_OPTIONS = [
  { value: "", label: "Distance" },
  { value: "condition", label: "Condition" },
  { value: "access_confidence", label: "Access confidence" },
  { value: "recommendation", label: "Recommended" },
];

export default function FilterPanel({ filters, onChange, sports }) {
  function update(patch) {
    onChange({ ...filters, ...patch });
  }

  return (
    <div className="filter-panel">
      <div className="filter-group">
        <label htmlFor="filter-sport">Sport</label>
        <select
          id="filter-sport"
          value={filters.sport}
          onChange={(e) => update({ sport: e.target.value })}
        >
          <option value="">Any sport</option>
          {sports.map((sport) => (
            <option key={sport} value={sport}>
              {sport}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="filter-access">Access</label>
        <select
          id="filter-access"
          value={filters.access}
          onChange={(e) => update({ access: e.target.value })}
        >
          {ACCESS_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="filter-radius">Radius</label>
        <select
          id="filter-radius"
          value={filters.radius}
          onChange={(e) => update({ radius: Number(e.target.value) })}
        >
          {RADII.map((radius) => (
            <option key={radius} value={radius}>
              {radius} miles
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="filter-sort">Sort by</label>
        <select
          id="filter-sort"
          value={filters.sort}
          onChange={(e) => update({ sort: e.target.value })}
        >
          {SORT_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
