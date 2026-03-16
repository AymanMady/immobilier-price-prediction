"use client"

import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet"
import "leaflet/dist/leaflet.css"
import L from "leaflet"
import { useEffect } from "react"

// Fix for default marker icon in leaflet
const DefaultIcon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
})

L.Marker.prototype.options.icon = DefaultIcon

// Neighborhood coordinates (approximate for Nouakchott)
const NEIGHBORHOOD_COORDS: Record<string, [number, number]> = {
  "Tevragh Zeina": [18.1065, -15.9754],
  "Arafat": [18.0494, -15.9461],
  "Ksar": [18.0934, -15.9626],
  "Sebkha": [18.0772, -15.9868],
  "Teyarett": [18.1384, -15.9526],
  "Dar Naim": [18.1054, -15.9081],
  "Toujounine": [18.0824, -15.9011],
  "Riyad": [18.0194, -15.9561],
  "El Mina": [18.0672, -15.9818],
}

function RecenterMap({ coords }: { coords: [number, number] }) {
  const map = useMap()
  useEffect(() => {
    map.setView(coords)
  }, [coords, map])
  return null
}

export default function InteractiveMap({ selectedQuartier }: { selectedQuartier: string }) {
  const coords = NEIGHBORHOOD_COORDS[selectedQuartier] || [18.0894, -15.9754] // Fallback to Nouakchott center

  return (
    <div className="w-full h-full min-h-[400px] rounded-2xl overflow-hidden border border-white/10 shadow-2xl">
      <MapContainer 
        center={coords} 
        zoom={13} 
        scrollWheelZoom={false}
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          className="map-tiles"
        />
        <Marker position={coords}>
          <Popup>
            {selectedQuartier || "Nouakchott"}
          </Popup>
        </Marker>
        <RecenterMap coords={coords} />
      </MapContainer>
      
      {/* Overlay styling for dark mode appearance */}
      <style jsx global>{`
        .leaflet-tile {
          filter: invert(100%) hue-rotate(180deg) brightness(95%) contrast(90%);
        }
        .leaflet-container {
          background: #09090b !important;
        }
      `}</style>
    </div>
  )
}
