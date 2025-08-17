const map = L.map('map').setView([51.1657, 10.4515], 6);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

let alertLayers = {};
let alertCount = 0;

let ws = null;
const statusElement = document.getElementById('status');
const counterElement = document.getElementById('counter');

const WS_URL = 'ws://localhost:8000/ws/global_map';

function updateStatus(status, message) {
    statusElement.className = `connection-status status-${status}`;
    statusElement.textContent = message;
}

function updateCounter() {
    counterElement.textContent = `Alerts: ${alertCount}`;
}

function connectWebSocket() {
    updateStatus('connecting', 'Connecting...');

    try {
        ws = new WebSocket(WS_URL);

        ws.onopen = function (event) {
            updateStatus('connected', 'Connected');
        };

        ws.onmessage = function (event) {
            try {
                let data;

                if (event.data instanceof ArrayBuffer) {
                    const buffer = new Uint8Array(event.data);
                    const header = new TextDecoder().decode(buffer.slice(0, 5));

                    if (header === 'gzip:') {
                        const compressed = buffer.slice(5);
                        const decompressed = pako.inflate(compressed, { to: 'string' });
                        data = JSON.parse(decompressed);
                    } else {
                        console.error('Unknown binary data format');
                        return;
                    }
                } else if (event.data instanceof Blob) {
                    const reader = new FileReader();
                    reader.onload = function () {
                        const buffer = new Uint8Array(reader.result);
                        const header = new TextDecoder().decode(buffer.slice(0, 5));

                        if (header === 'gzip:') {
                            const compressed = buffer.slice(5);
                            const decompressed = pako.inflate(compressed, { to: 'string' });
                            const data = JSON.parse(decompressed);
                            processAlertsData(data);
                        }
                    };
                    reader.readAsArrayBuffer(event.data);
                    return;
                } else {
                    data = JSON.parse(event.data);
                }

                processAlertsData(data);

            } catch (error) {
                console.error('Error processing WebSocket message:', error);
                console.error('Event data type:', typeof event.data);
                console.error('Event data:', event.data);
            }
        };

        function processAlertsData(data) {

            if (Array.isArray(data)) {
                clearAllAlerts();

                data.forEach((alert, index) => {
                    addAlert(alert);
                });

                alertCount = data.length;
                updateCounter();
            } else {
                console.warn('Received data is not an array:', data);
            }
        }

        ws.onclose = function (event) {
            console.log('WebSocket disconnected');
            updateStatus('disconnected', 'Disconnected');

            setTimeout(connectWebSocket, 5000);
        };

        ws.onerror = function (error) {
            console.error('WebSocket error:', error);
            updateStatus('disconnected', 'Connection Error');
        };

    } catch (error) {
        console.error('Error creating WebSocket:', error);
        updateStatus('disconnected', 'Connection Failed');
        setTimeout(connectWebSocket, 5000);
    }
}

function clearAllAlerts() {
    Object.values(alertLayers).forEach(layer => {
        map.removeLayer(layer);
    });
    alertLayers = {};
}

function addAlert(alert) {
    try {

        const {
            event,
            severity,
            event_code,
            event_code_icon_url,
            location,
            html_tooltip,
            html_popup,
            geojson,
            style_props
        } = alert;

        if (!location || !Array.isArray(location) || location.length < 2) {
            console.error('Invalid location data:', location);
            return;
        }

        const lat = parseFloat(location[0]);
        const lng = parseFloat(location[1]);

        if (isNaN(lat) || isNaN(lng)) {
            console.error('Invalid coordinates:', location);
            return;
        }

        const alertId = `${event_code || 'unknown'}_${lat}_${lng}_${Date.now()}`;

        if (alertLayers[alertId]) {
            map.removeLayer(alertLayers[alertId]);
        }

        const alertLayerGroup = L.layerGroup();

        if (geojson && geojson.features && geojson.features.length > 0) {
            try {
                const geoJsonLayer = L.geoJSON(geojson, {
                    style: {
                        color: (style_props && style_props.strokeColor) || 'red',
                        weight: (style_props && style_props.strokeWeight) || 2,
                        fillColor: (style_props && style_props.fillColor) || 'yellow',
                        fillOpacity: (style_props && style_props.fillOpacity) || 0.3,
                        opacity: 0.8
                    },
                    onEachFeature: function (feature, layer) {
                        if (html_popup) {
                            layer.bindPopup(html_popup, {
                                maxHeight: 300
                            });
                        }
                        if (html_tooltip) {
                            layer.bindTooltip(html_tooltip, {
                                sticky: true
                            });
                        }
                    }
                });

                alertLayerGroup.addLayer(geoJsonLayer);
            } catch (geoError) {
                console.error('Error creating GeoJSON layer:', geoError);
            }
        } else {
            console.warn('No valid GeoJSON data found');
        }

        let marker;
        try {
            if (event_code_icon_url && event_code_icon_url.startsWith('http')) {

                const customIcon = L.icon({
                    iconUrl: event_code_icon_url,
                    iconSize: [32, 32],
                    iconAnchor: [16, 16],
                    popupAnchor: [0, -16],
                    shadowSize: [41, 41],
                    shadowAnchor: [12, 41]
                });

                marker = L.marker([lat, lng], {
                    icon: customIcon
                });
            } else {
                marker = L.circleMarker([lat, lng], {
                    radius: 8,
                    fillColor: '#ffff00',
                    color: 'red',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.8
                });
            }

            if (html_popup) {
                marker.bindPopup(html_popup);
            }
            if (html_tooltip) {
                marker.bindTooltip(html_tooltip, {
                    sticky: true
                });
            }

            alertLayerGroup.addLayer(marker);

        } catch (markerError) {
            console.error('Error creating marker:', markerError);
        }

        if (alertLayerGroup.getLayers().length > 0) {
            alertLayerGroup.addTo(map);
            alertLayers[alertId] = alertLayerGroup;
        } else {
            console.warn('No layers were added to the alert group');
        }

    } catch (error) {
        console.error('Error adding alert:', error, alert);
    }
}

/*
TODO: fix the following code snippet
map.on('zoomend', function () {
    const currentZoom = map.getZoom();

    Object.values(alertLayers).forEach(layerGroup => {
        layerGroup.eachLayer(layer => {
            if (layer._isCustomIcon && currentZoom < 8) {
                layerGroup.removeLayer(layer);
            } else if (layer._isCircleMarker && currentZoom < 6) {
                layerGroup.removeLayer(layer);
            } else if (layer.feature && currentZoom < 7) {
                layerGroup.removeLayer(layer);
            } else if (!layerGroup.hasLayer(layer)) {
                layerGroup.addLayer(layer);
            }
        });
    });
});*/

connectWebSocket();

document.addEventListener('keydown', function (event) {
    if (event.key.toLowerCase() === 'r') {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send('refresh');
            console.log('Sent refresh command to server');
        } else {
            console.log('WebSocket not connected');
        }
    }
});