import { forwardRef, useEffect, useImperativeHandle, useRef } from "react";
import { MAP_MESSAGE_TYPES, toMapResult } from "../utils/mapMessaging.js";

const MAP_FRAME_URL = import.meta.env.VITE_MAP_FRAME_URL || "/map-frame/index.html";

/**
 * Owns the map iframe boundary. All map rendering happens inside the
 * embedded document; this component only exchanges postMessage events
 * with it, per the SET_RESULTS / MARKER_SELECTED contract.
 */
const MapFrame = forwardRef(function MapFrame({ results, onMarkerSelected }, ref) {
  const iframeRef = useRef(null);
  const readyRef = useRef(false);
  const pendingResultsRef = useRef(null);

  useEffect(() => {
    function handleMessage(event) {
      const iframe = iframeRef.current;
      if (!iframe || event.source !== iframe.contentWindow) return;

      const data = event.data || {};

      if (data.type === MAP_MESSAGE_TYPES.MAP_READY) {
        readyRef.current = true;
        if (pendingResultsRef.current) {
          postResults(pendingResultsRef.current);
        }
      } else if (data.type === MAP_MESSAGE_TYPES.MARKER_SELECTED) {
        onMarkerSelected?.(data.facility_id);
      }
    }

    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, [onMarkerSelected]);

  function postResults(mapResults) {
    const iframe = iframeRef.current;
    if (!iframe?.contentWindow) return;
    iframe.contentWindow.postMessage(
      { type: MAP_MESSAGE_TYPES.SET_RESULTS, results: mapResults },
      "*"
    );
  }

  useEffect(() => {
    const mapResults = results.map(toMapResult);
    if (readyRef.current) {
      postResults(mapResults);
    } else {
      pendingResultsRef.current = mapResults;
    }
  }, [results]);

  useImperativeHandle(ref, () => ({
    selectMarker(facilityId) {
      const iframe = iframeRef.current;
      if (!iframe?.contentWindow) return;
      iframe.contentWindow.postMessage(
        { type: MAP_MESSAGE_TYPES.SELECT_MARKER, facility_id: facilityId },
        "*"
      );
    },
  }));

  return (
    <iframe
      ref={iframeRef}
      title="Facility map"
      src={MAP_FRAME_URL}
      className="map-frame"
      loading="lazy"
    />
  );
});

export default MapFrame;
