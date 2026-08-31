const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      // ignore body parse failures
    }
    throw new Error(detail || `Request failed (${response.status})`);
  }

  return response.json();
}

export function search({ lat, lon, radius, q, sport, access, sort }) {
  const params = new URLSearchParams({ lat, lon, radius });
  if (q) params.set("q", q);
  if (sport) params.set("sport", sport);
  if (access) params.set("access", access);
  if (sort) params.set("sort", sort);
  return request(`/api/search?${params.toString()}`);
}

export function getFacility(id) {
  return request(`/api/facilities/${encodeURIComponent(id)}`);
}

export function getSports() {
  return request("/api/sports");
}

export function submitReport(facilityId, report) {
  return request(`/api/facilities/${encodeURIComponent(facilityId)}/reports`, {
    method: "POST",
    body: JSON.stringify(report),
  });
}

export function classifyAccess(payload) {
  return request("/api/ai/classify-access", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getHealth() {
  return request("/api/health");
}
