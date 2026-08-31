import { useEffect, useState } from "react";
import { getFacility } from "../api/client.js";
import FacilityDetails from "../components/FacilityDetails.jsx";
import LoadingState from "../components/LoadingState.jsx";

/** Standalone facility view, used when a facility ID is shared/deep-linked. */
export default function FacilityPage({ facilityId, onBack }) {
  const [facility, setFacility] = useState(null);
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    let cancelled = false;
    setStatus("loading");
    getFacility(facilityId)
      .then((data) => {
        if (!cancelled) {
          setFacility(data);
          setStatus("success");
        }
      })
      .catch(() => {
        if (!cancelled) setStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, [facilityId]);

  if (status === "loading") return <LoadingState label="Loading facility…" />;
  if (status === "error" || !facility) {
    return (
      <div className="empty-state error">
        <p>Facility not found.</p>
        <button type="button" onClick={onBack}>
          Back to search
        </button>
      </div>
    );
  }

  return <FacilityDetails facility={facility} onClose={onBack} />;
}
