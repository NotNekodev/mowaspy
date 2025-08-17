from plug import CountryPlugin
from typing import List, Any
import shapely.geometry as shape
import requests
import logging

def to_geojson_polygon(coordinates):
    if coordinates[0] != coordinates[-1]:
        coordinates.append(coordinates[0])
    
    geojson = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [coordinates]
        },
        "properties": {}
    }
    return geojson

class CountryPluginSE(CountryPlugin):
    
#alert_data = {
#                                    "event": actual_info["event"],
#                                    "severity": severity,
#                                    "event_code": event_code,
#                                    "event_code_icon_url": event_code_icon_url,
#                                    "location": [centroid.y, centroid.x],
#                                    "html_tooltip": html_tooltip,
#                                    "html_popup": html,
#                                    "geojson": geojson_data,
#                                    "style_props": {
#                                        "strokeColor": properties.get("strokeColor", "red"),
#                                        "strokeWeight": properties.get("strokeWeight", 2),
#                                        "fillColor": properties.get("fillColor", "yellow"),
#                                        "fillOpacity": 0.5
#                                    }

    def initialize(self) -> None:
        self.alerts = []
        self.url = "https://opendata-download-warnings.smhi.se/ibww/api/version/1/warning.json"
        self.logger = logging.getLogger("nocto-plug-se")
        
        response = requests.get(self.url)

        if response.status_code == 200:
            for alert in response.json():
                event = alert["event"].get("en", "Unknown")
                severity = alert["warningAreas"][0]["warningLevel"].get("en", "Unknown")
                event_code = alert["event"].get("code", "Unknown")
                event_code_icon_url = "pippis"
                geojson = alert["warningAreas"][0]["area"]

                polygon = shape.geo.shape(geojson)
                centroid = polygon.centroid

                description_text = ""

                for description in alert["warningAreas"][0]["descriptions"]:
                    description_text += f"{description["title"].get("en", "Unknown")}<br>"
                    description_text += f"{description["text"].get("en", "Unknown")}<br>"
                    description_text += f"<br><hr><br>"

                html = f"""
                <style>
                .title {{
                    color: {"blue" if event_code == "MESSAGE" else "white"};
                }}
                body {{
                    background-color: black;
                    color: white;
                }}
                </style>
                <b class="title">{alert["warningAreas"][0]["eventDescription"].get("en", "Unknown")}</b><br><br>
                {description_text}
                """

                html_tooltip = f"""
                <style>
                .title {{
                    color: {"blue" if event_code == "MESSAGE" else "white"};
                }}
                </style>
                <b class="title">{alert["warningAreas"][0]["eventDescription"].get("en", "Unknown")}<br></b>
                <p class=""><i>{alert["event"].get("en", "Unknown")}</i></p>
                """

                stroke_color = "blue" if event_code == "MESSAGE" else "red"
                stroke_weight = 2
                fill_color = "blue" if event_code == "MESSAGE" else "red"
                fill_opacity = 0.5

                alert_data = {
                    "event": event,
                    "severity": severity,
                    "event_code": event_code,
                    "event_code_icon_url": event_code_icon_url,
                    "location": [centroid.y, centroid.x],
                    "html_tooltip": html_tooltip,
                    "html_popup": html,
                    "geojson": geojson,
                    "style_props": {
                        "strokeColor": stroke_color,
                        "strokeWeight": stroke_weight,
                        "fillColor": fill_color,
                        "fillOpacity": fill_opacity
                    }
                }

                self.alerts.append(alert_data)
        else:
            self.logger.error(f"Failed to retrieve alerts: {response.status_code}")

    def get_country_code(self) -> str:
        return "SE"

    def add_alerts_to_map(self, map_object: Any) -> None:
        pass

    def refresh_alerts_on_map(self, map_object: Any) -> None:
        self.alerts = []
        
        response = requests.get(self.url)

        if response.status_code == 200:
            for alert in response.json():
                event = alert["event"].get("en", "Unknown")
                severity = alert["warningAreas"][0]["warningLevel"].get("en", "Unknown")
                warning_code = alert["warningAreas"][0]["warningLevel"].get("code", "Unknown")
                event_code = alert["event"].get("code", "Unknown")
                event_code_icon_url = "pippis"
                geojson = alert["warningAreas"][0].get("area", {})

                polygon = shape.geo.shape(geojson)
                centroid = polygon.centroid

                description_text = ""

                for description in alert["warningAreas"][0]["descriptions"]:
                    description_text += f"{description["title"].get("en", "Unknown")}:<br>"
                    description_text += f"{description["text"].get("en", "Unknown")}<br>"
                    description_text += f"<br><hr><br>"

                html = f"""
                <style>
                .title {{
                    color: {"#3d7aff" if warning_code == "MESSAGE" else "white"};
                }}
                body {{
                    background-color: black;
                    color: white;
                }}
                </style>
                <b class="title">{alert["warningAreas"][0]["eventDescription"].get("en", "Unknown")}</b><br><br>
                {description_text}
                """

                html_tooltip = f"""
                <style>
                .title {{
                    color: {"#3d7aff" if warning_code == "MESSAGE" else "white"};
                }}
                </style>
                <b class="title">{alert["warningAreas"][0]["eventDescription"].get("en", "Unknown")}<br></b>
                <p class=""><i>{alert["event"].get("en", "Unknown")}</i></p>
                """

                stroke_color = "#3d7aff" if warning_code == "MESSAGE" else "white"
                stroke_weight = 2
                fill_color = "#3d7aff" if warning_code == "MESSAGE" else "white"
                fill_opacity = 0.5

                alert_data = {
                    "event": event,
                    "severity": severity,
                    "event_code": event_code,
                    "event_code_icon_url": event_code_icon_url,
                    "location": [centroid.y, centroid.x],
                    "html_tooltip": html_tooltip,
                    "html_popup": html,
                    "geojson": geojson,
                    "style_props": {
                        "strokeColor": stroke_color,
                        "strokeWeight": stroke_weight,
                        "fillColor": fill_color,
                        "fillOpacity": fill_opacity
                    }
                }

                self.alerts.append(alert_data)
        else:
            self.logger.error(f"Failed to retrieve alerts: {response.status_code}")

    def get_alerts(self) -> List[Any]:
        return self.alerts