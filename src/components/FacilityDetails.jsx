import { useState } from "react";
import AccessBadge from "./AccessBadge.jsx";
import ConditionBadge from "./ConditionBadge.jsx";
import { submitReport } from "../api/client.js";

const REPORT_TYPES = [
  { value: "condition", label: "Condition report" },
  { value: "access", label: "Access correction" },
  { value: "hours", label: "Hours correction" },
  { value: "general", label: "General note" },
];

export default function FacilityDetails({ facility, onClose }) {
  const [reportType, setReportType] = useState("condition");
  const [description, setDescription] = useState("");
  const [condition, setCondition] = useState("");
  const [submitStatus, setSubmitStatus] = useState("idle");
  const [submitError, setSubmitError] = useState(null);

  if (!facility) return null;

  async function handleSubmitReport(event) {
    event.preventDefault();
    if (!description.trim()) {
      setSubmitError("Please describe what you observed.");
      return;
    }

    setSubmitStatus("submitting");
    setSubmitError(null);

    try {
      await submitReport(facility.id, {
        report_type: reportType,
        description: description.trim(),
        condition: reportType === "condition" ? condition || null : null,
      });
      setSubmitStatus("success");
      setDescription("");
      setCondition("");
    } catch (err) {
      setSubmitStatus("error");
      setSubmitError(err.message || "Could not submit report.");
    }
  }

  return (
    <aside className="facility-details" aria-label="Facility details">
      <button type="button" className="close-button" onClick={onClose} aria-label="Close details">
        ×
      </button>

      <h2>{facility.name}</h2>
      <p className="facility-sports">
        {(facility.sport_types || []).join(", ") || facility.facility_type}
      </p>

      <div className="facility-badges">
        <AccessBadge access={facility.access} />
        <ConditionBadge condition={facility.condition} />
      </div>

      {facility.access?.evidence && (
        <p className="evidence">
          <strong>Access evidence:</strong> {facility.access.evidence}
        </p>
      )}

      <dl className="detail-grid">
        <dt>Hours</dt>
        <dd>{facility.hours?.display || "Unknown"}</dd>

        <dt>Surface</dt>
        <dd>{facility.surface || "Unknown"}</dd>

        <dt>Operator</dt>
        <dd>{facility.operator || "Unknown"}</dd>

        <dt>Address</dt>
        <dd>
          {[facility.address?.street, facility.address?.city, facility.address?.state]
            .filter(Boolean)
            .join(", ") || "Unknown"}
        </dd>

        <dt>Last updated</dt>
        <dd>{facility.updated_at ? new Date(facility.updated_at).toLocaleDateString() : "Unknown"}</dd>

        <dt>OSM ID</dt>
        <dd>{facility.osm?.id ? `${facility.osm.type}/${facility.osm.id}` : "N/A"}</dd>
      </dl>

      {facility.website && (
        <p>
          <a href={facility.website} target="_blank" rel="noreferrer noopener">
            Visit website
          </a>
        </p>
      )}

      <form className="report-form" onSubmit={handleSubmitReport}>
        <h3>Report a correction</h3>

        <label htmlFor="report-type">Report type</label>
        <select id="report-type" value={reportType} onChange={(e) => setReportType(e.target.value)}>
          {REPORT_TYPES.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        {reportType === "condition" && (
          <>
            <label htmlFor="report-condition">Observed condition</label>
            <select
              id="report-condition"
              value={condition}
              onChange={(e) => setCondition(e.target.value)}
            >
              <option value="">Select condition</option>
              <option value="excellent">Excellent</option>
              <option value="good">Good</option>
              <option value="fair">Fair</option>
              <option value="poor">Poor</option>
            </select>
          </>
        )}

        <label htmlFor="report-description">Description</label>
        <textarea
          id="report-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={2000}
          rows={3}
        />

        <button type="submit" disabled={submitStatus === "submitting"}>
          {submitStatus === "submitting" ? "Submitting…" : "Submit report"}
        </button>

        {submitStatus === "success" && <p className="success-message">Thanks — report submitted.</p>}
        {submitError && (
          <p className="field-error" role="alert">
            {submitError}
          </p>
        )}
      </form>
    </aside>
  );
}
