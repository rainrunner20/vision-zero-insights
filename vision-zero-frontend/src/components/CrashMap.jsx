import { useEffect, useRef } from "react";
import mapboxgl from "mapbox-gl";
import { fetchCrashData } from "../api/crashAPI";
import "mapbox-gl/dist/mapbox-gl.css";

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_PUBLIC_TOKEN || '';

export default function CrashMap({ onMarkerClick }) {
  const mapRef = useRef(null);

  useEffect(() => {
    if (!import.meta.env.VITE_MAPBOX_PUBLIC_TOKEN || !mapRef.current) return undefined;
    const map = new mapboxgl.Map({
      container: mapRef.current,
      style: "mapbox://styles/mapbox/streets-v11",
      center: [-73.935242, 40.73061],
      zoom: 10,
    });

    map.on("load", async () => {
      const data = await fetchCrashData();
      console.log("🗺️ Fetched crash data:", data);

      // Show markers
      data.forEach((d) => {
        if (d.longitude && d.latitude) {
          const marker = new mapboxgl.Marker()
            .setLngLat([d.longitude, d.latitude])
            .addTo(map);
          marker.getElement().addEventListener("click", () => onMarkerClick(d));
        }
      });

      // Build GeoJSON
      const geojson = {
        type: "FeatureCollection",
        features: data
          .filter((d) => d.longitude && d.latitude)
          .map((d) => ({
            type: "Feature",
            properties: {
              injuries: d.number_of_persons_injured || 1,
            },
            geometry: {
              type: "Point",
              coordinates: [parseFloat(d.longitude), parseFloat(d.latitude)],
            },
          })),
      };

      console.log("🔥 GeoJSON features for heatmap:", geojson.features.length);

      map.addSource("crash-heat", {
        type: "geojson",
        data: geojson,
      });

      map.addLayer({
        id: "crash-heatmap",
        type: "heatmap",
        source: "crash-heat",
        maxzoom: 15,
        paint: {
          "heatmap-weight": ["interpolate", ["linear"], ["get", "injuries"], 0, 0, 5, 1],
          "heatmap-intensity": ["interpolate", ["linear"], ["zoom"], 0, 1, 15, 3],
          "heatmap-color": [
            "interpolate",
            ["linear"],
            ["heatmap-density"],
            0, "rgba(0,0,255,0)",
            0.2, "royalblue",
            0.4, "cyan",
            0.6, "lime",
            0.8, "yellow",
            1, "red"
          ],
          "heatmap-radius": ["interpolate", ["linear"], ["zoom"], 0, 2, 15, 20],
        },
      });
    });

    return () => map.remove();
  }, [onMarkerClick]);

  if (!import.meta.env.VITE_MAPBOX_PUBLIC_TOKEN) {
    return <div role="status" className="p-8 text-slate-700">
      Map visualization is not configured. Add a restricted Mapbox public token to VITE_MAPBOX_PUBLIC_TOKEN.
    </div>;
  }
  return <div ref={mapRef} className="w-full h-[calc(100vh-64px)]" />;
}
