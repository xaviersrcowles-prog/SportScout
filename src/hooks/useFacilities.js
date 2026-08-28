import { useEffect, useState } from "react";
import { getSports } from "../api/client.js";

export function useSportsList() {
  const [sports, setSports] = useState([]);

  useEffect(() => {
    let cancelled = false;
    getSports()
      .then((data) => {
        if (!cancelled) setSports(data.sports || []);
      })
      .catch(() => {
        if (!cancelled) setSports([]);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return sports;
}
