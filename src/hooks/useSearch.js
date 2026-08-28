import { useCallback, useState } from "react";
import { search } from "../api/client.js";

const DEFAULT_RADIUS = 5;

export function useSearch() {
  const [results, setResults] = useState([]);
  const [status, setStatus] = useState("idle"); // idle | loading | success | error
  const [error, setError] = useState(null);
  const [center, setCenter] = useState(null);

  const runSearch = useCallback(async (params) => {
    setStatus("loading");
    setError(null);

    try {
      const response = await search({ radius: DEFAULT_RADIUS, ...params });
      setResults(response.results || []);
      setCenter({ lat: params.lat, lon: params.lon });
      setStatus("success");
    } catch (err) {
      setError(err.message || "Search failed.");
      setStatus("error");
    }
  }, []);

  return { results, status, error, center, runSearch, setResults };
}
