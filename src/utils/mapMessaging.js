/** Shared message-type constants for the parent <-> iframe map contract. */

export const MAP_MESSAGE_TYPES = {
  SET_RESULTS: "SET_RESULTS",
  SELECT_MARKER: "SELECT_MARKER",
  MARKER_SELECTED: "MARKER_SELECTED",
  MAP_READY: "MAP_READY",
};

export function toMapResult(facility) {
  return {
    id: facility.id,
    lat: facility.latitude,
    lon: facility.longitude,
    name: facility.name,
    access: facility.access?.classification || "unknown",
  };
}

export function isTrustedOrigin(eventOrigin, expectedOrigin) {
  if (!expectedOrigin) return true;
  return eventOrigin === expectedOrigin;
}
