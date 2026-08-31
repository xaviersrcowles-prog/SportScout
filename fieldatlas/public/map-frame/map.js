/**
 * Embedded map document (the iframe half of the SportScout map contract).
 *
 * Listens for postMessage events from the parent React app, renders/updates
 * markers with Leaflet + OpenStreetMap tiles, and reports marker selection
 * back to the parent. This file intentionally has no build step so it can
 * be served as a static document independent of the React bundle.
 */

(function () {
  var map = L.map("map", { zoomControl: true }).setView([42.3601, -71.0589], 9);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  // Search results can include thousands of unnamed OSM pitches/courts, so
  // markers are clustered rather than added to the map directly.
  var clusterGroup = L.markerClusterGroup({
    maxClusterRadius: 50,
    spiderfyOnMaxZoom: true,
    disableClusteringAtZoom: 17,
  });
  map.addLayer(clusterGroup);

  var markersById = {};
  var selectedId = null;
  var parentOrigin = null;

  function accessClass(access) {
    var known = ["public", "restricted", "members_only", "private", "unknown"];
    return known.indexOf(access) === -1 ? "unknown" : access;
  }

  function iconFor(facility, isSelected) {
    var cls = "facility-marker access-" + accessClass(facility.access);
    if (isSelected) cls += " selected";
    return L.divIcon({
      className: "",
      html: '<div class="' + cls + '"><span></span></div>',
      iconSize: isSelected ? [34, 34] : [26, 26],
      iconAnchor: isSelected ? [17, 34] : [13, 26],
    });
  }

  function clearMarkers() {
    clusterGroup.clearLayers();
    markersById = {};
  }

  function setResults(results) {
    clearMarkers();
    selectedId = null;

    var newMarkers = [];

    (results || []).forEach(function (facility) {
      if (typeof facility.lat !== "number" || typeof facility.lon !== "number") return;

      var marker = L.marker([facility.lat, facility.lon], {
        icon: iconFor(facility, false),
      });

      marker._facilityData = facility;
      marker.bindTooltip(facility.name || "Facility", { direction: "top" });

      marker.on("click", function () {
        selectMarker(facility.id, { fromMap: true });
      });

      newMarkers.push(marker);
      markersById[facility.id] = marker;
    });

    clusterGroup.addLayers(newMarkers);
    fitToResults(results);
  }

  function selectMarker(facilityId, options) {
    options = options || {};

    if (selectedId && markersById[selectedId]) {
      var prevMarker = markersById[selectedId];
      prevMarker.setIcon(iconFor(prevMarker._facilityData || {}, false));
    }

    selectedId = facilityId;
    var marker = markersById[facilityId];
    if (marker) {
      marker.setIcon(iconFor(marker._facilityData || {}, true));
      clusterGroup.zoomToShowLayer(marker, function () {
        map.panTo(marker.getLatLng());
      });
    }

    if (options.fromMap) {
      postToParent({ type: "MARKER_SELECTED", facility_id: facilityId });
    }
  }

  function fitToResults(results) {
    var coords = (results || [])
      .filter(function (f) {
        return typeof f.lat === "number" && typeof f.lon === "number";
      })
      .map(function (f) {
        return [f.lat, f.lon];
      });

    if (coords.length === 0) return;

    if (coords.length === 1) {
      map.setView(coords[0], 13);
      return;
    }

    map.fitBounds(L.latLngBounds(coords), { padding: [40, 40] });
  }

  function postToParent(message) {
    var target = parentOrigin || "*";
    window.parent.postMessage(message, target);
  }

  window.addEventListener("message", function (event) {
    var data = event.data || {};

    if (data.type === "SET_RESULTS") {
      parentOrigin = event.origin;
      setResults(data.results || []);
    } else if (data.type === "SELECT_MARKER") {
      parentOrigin = event.origin;
      selectMarker(data.facility_id, { fromMap: false });
    } else if (data.type === "FIT_RESULTS") {
      parentOrigin = event.origin;
    }
  });

  // Let the parent know the map is ready to receive messages.
  postToParent({ type: "MAP_READY" });
})();
