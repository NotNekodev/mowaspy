from plug import CountryPlugin
from typing import Any, List
import folium
import requests
from folium import IFrame
import shapely.geometry as shape
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s[%(levelname)s]: %(message)s')

class CountryPluginDE(CountryPlugin):

    def initialize(self) -> None:
        self.alerts = []
        self.logger = logging.getLogger("nocto-plug-de")
        base_url = "https://warnung.bund.de/api31/"
        
        for warning_provider in ["dwd", "katwarn", "mowas", "police", "lhp", "biwapp"]:
            url = f"{base_url}/{warning_provider}/mapData.json"
            response = requests.get(url)
            if response.status_code == 200:
                warnings = response.json()
                
                for idx, warning in enumerate(warnings):
                    
                    geojson_url = f"{base_url}/warnings/{warning['id']}.geojson"
                    geojson_response = requests.get(geojson_url)

                    info_url = f"{base_url}/warnings/{warning['id']}.json"
                    info_response = requests.get(info_url)

                    if info_response.status_code == 200:
                        info_data = info_response.json()
                        actual_info = info_data["info"][0]

                        event = actual_info["event"]
                        severity = actual_info["severity"]
                        event_code = actual_info["eventCode"][0].get(
                            "value", "Unknown Event Code"
                        )

                        if warning["id"].startswith("dwd"):
                            event_code_icon_url = f"{base_url}appdata/gsb/eventCodes/BBK-EVC-062.png"
                        else:
                            event_code_icon_url = f"{base_url}appdata/gsb/eventCodes/{event_code}.png"

                        if geojson_response.status_code == 200:
                            geojson_data = geojson_response.json()

                            if geojson_data.get("features"):
                                feature = geojson_data["features"][0]
                                properties = feature.get("properties", {})

                                html = f"""
                                <style>
                                .title {{
                                    color: {properties.get("fillColor", "white")};
                                }}
                                body {{
                                    background-color: black;
                                    color: white;
                                }}
                                </style>
                                <b class="title">{actual_info["headline"]}</b><br><br>
                                {actual_info["description"]}
                                """

                                html_tooltip = f"""
                                <style>
                                .title {{
                                    color: {properties.get("fillColor", "white")};
                                }}
                                </style>
                                <b class="title">{actual_info["headline"]}<br></b>
                                <p class=""><i>{actual_info["event"]}</i></p>
                                """

                                geometry = feature.get("geometry", {})
                                geom_type = geometry.get("type")
                                coordinates = geometry.get("coordinates", [])
                                
                                if geom_type == "Polygon" and coordinates:
                                    try:
                                        polygon = shape.Polygon(
                                            [(point[0], point[1]) for point in coordinates[0]]
                                        )
                                        centroid = polygon.centroid
                                    except Exception as e:
                                        centroid = type('obj', (object,), {'y': 51.0, 'x': 10.0})()
                                elif geom_type == "MultiPolygon" and coordinates:
                                    try:
                                        polygons = [shape.Polygon(p[0]) for p in coordinates]
                                        multi = shape.MultiPolygon(polygons)
                                        centroid = multi.centroid
                                    except Exception as e:
                                        centroid = type('obj', (object,), {'y': 51.0, 'x': 10.0})()
                                else:
                                    centroid = type('obj', (object,), {'y': 51.0, 'x': 10.0})()

                                alert_data = {
                                    "event": actual_info["event"],
                                    "severity": severity,
                                    "event_code": event_code,
                                    "event_code_icon_url": event_code_icon_url,
                                    "location": [centroid.y, centroid.x],
                                    "html_tooltip": html_tooltip,
                                    "html_popup": html,
                                    "geojson": geojson_data,
                                    "style_props": {
                                        "strokeColor": properties.get("strokeColor", "red"),
                                        "strokeWeight": properties.get("strokeWeight", 2),
                                        "fillColor": properties.get("fillColor", "yellow"),
                                        "fillOpacity": 0.5
                                    }
                                }
                                self.alerts.append(alert_data)
                            else:
                                self.logger.warning(f"      No features in GeoJSON")
                        else:
                            self.logger.error(f"      Failed to load GeoJSON: {geojson_response.status_code}")
                    else:
                        self.logger.error(f"      Failed to load warning info: {info_response.status_code}")
            else:
                self.logger.error(f"  Error fetching warnings from {warning_provider}: {response.status_code}")


    def get_country_code(self) -> str:
        return "DE"

    def add_alerts_to_map(self, map_object: Any) -> None:
        
        for i, alert in enumerate(self.alerts):

            tooltip = folium.Tooltip(alert["html_tooltip"], sticky=True)
            iframe = IFrame(html=alert["html_popup"], width=300, height=300)
            popup = folium.Popup(iframe, max_width=400)

            event_code_icon = folium.CustomIcon(
                icon_image=alert["event_code_icon_url"],
                icon_size=(30, 30)
            )

            offset_lat = (i % 3 - 1) * 0.01
            offset_lng = ((i // 3) % 3 - 1) * 0.01
            adjusted_location = [
                alert["location"][0] + offset_lat,
                alert["location"][1] + offset_lng
            ]
            
            folium.Marker(
                location=adjusted_location,
                icon=event_code_icon,
                tooltip=tooltip,
                popup=popup,
            ).add_to(map_object)

            style_props = alert["style_props"].copy()
            
            try:
                gj = folium.GeoJson(
                    data=alert["geojson"],
                    style_function=lambda feature, props=style_props: {
                        "color": props["strokeColor"],
                        "weight": props["strokeWeight"],
                        "fillColor": props["fillColor"],
                        "fillOpacity": props["fillOpacity"],
                    },
                    tooltip=folium.Tooltip(alert["html_tooltip"], parse_html=True),
                    popup=folium.Popup(iframe, max_width=400),
                )
                gj.add_to(map_object)
                    
            except Exception as e:
                self.logger.error(f"  Error adding GeoJSON with custom style: {e}")

    def refresh_alerts_on_map(self, map_object: Any) -> None:
        self.alerts = []

        # clear current folium markers and polygons

        base_url = "https://warnung.bund.de/api31/"
        
        for warning_provider in ["dwd", "katwarn", "mowas", "police", "lhp", "biwapp"]:
            url = f"{base_url}/{warning_provider}/mapData.json"
            response = requests.get(url)
            if response.status_code == 200:
                warnings = response.json()
                for idx, warning in enumerate(warnings):
                    geojson_url = f"{base_url}/warnings/{warning['id']}.geojson"
                    geojson_response = requests.get(geojson_url)

                    info_url = f"{base_url}/warnings/{warning['id']}.json"
                    info_response = requests.get(info_url)

                    if info_response.status_code == 200:
                        info_data = info_response.json()
                        actual_info = info_data["info"][0]

                        event = actual_info["event"]
                        severity = actual_info["severity"]
                        event_code = actual_info["eventCode"][0].get(
                            "value", "Unknown Event Code"
                        )

                        if warning["id"].startswith("dwd"):
                            event_code_icon_url = f"{base_url}appdata/gsb/eventCodes/BBK-EVC-062.png"
                        else:
                            event_code_icon_url = f"{base_url}appdata/gsb/eventCodes/{event_code}.png"

                        if geojson_response.status_code == 200:
                            geojson_data = geojson_response.json()

                            if geojson_data.get("features"):
                                feature = geojson_data["features"][0]
                                properties = feature.get("properties", {})

                                html = f"""
                                <style>
                                .title {{
                                    color: {properties.get("fillColor", "white")};
                                }}
                                body {{
                                    background-color: black;
                                    color: white;
                                }}
                                </style>
                                <b class="title">{actual_info["headline"]}</b><br><br>
                                {actual_info["description"]}
                                """

                                html_tooltip = f"""
                                <style>
                                .title {{
                                    color: {properties.get("fillColor", "white")};
                                }}
                                </style>
                                <b class="title">{actual_info["headline"]}<br></b>
                                <p class=""><i>{actual_info["event"]}</i></p>
                                """

                                geometry = feature.get("geometry", {})
                                geom_type = geometry.get("type")
                                coordinates = geometry.get("coordinates", [])
                                
                                if geom_type == "Polygon" and coordinates:
                                    try:
                                        polygon = shape.Polygon(
                                            [(point[0], point[1]) for point in coordinates[0]]
                                        )
                                        centroid = polygon.centroid
                                    except Exception as e:
                                        centroid = type('obj', (object,), {'y': 51.0, 'x': 10.0})()
                                elif geom_type == "MultiPolygon" and coordinates:
                                    try:
                                        polygons = [shape.Polygon(p[0]) for p in coordinates]
                                        multi = shape.MultiPolygon(polygons)
                                        centroid = multi.centroid
                                    except Exception as e:
                                        centroid = type('obj', (object,), {'y': 51.0, 'x': 10.0})()
                                else:
                                    centroid = type('obj', (object,), {'y': 51.0, 'x': 10.0})()

                                alert_data = {
                                    "event": actual_info["event"],
                                    "severity": severity,
                                    "event_code": event_code,
                                    "event_code_icon_url": event_code_icon_url,
                                    "location": [centroid.y, centroid.x],
                                    "html_tooltip": html_tooltip,
                                    "html_popup": html,
                                    "geojson": geojson_data,
                                    "style_props": {
                                        "strokeColor": properties.get("strokeColor", "red"),
                                        "strokeWeight": properties.get("strokeWeight", 2),
                                        "fillColor": properties.get("fillColor", "yellow"),
                                        "fillOpacity": 0.5
                                    }
                                }
                                self.alerts.append(alert_data)
                            else:
                                self.logger.warning(f"      No features in GeoJSON")
                        else:
                            self.logger.error(f"      Failed to load GeoJSON: {geojson_response.status_code}")
                    else:
                        self.logger.error(f"      Failed to load warning info: {info_response.status_code}")
            else:
                self.logger.error(f"  Error fetching warnings from {warning_provider}: {response.status_code}")

    def get_alerts(self) -> List[Any]:
        return self.alerts
