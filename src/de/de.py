import folium
import requests
from folium import IFrame
import shapely.geometry as shape

def add_de_warnings(m):

    custom_css = """
    <style>
    .leaflet-popup-content-wrapper {
        background-color: black;
        color: white;
        border-radius: 6px;
    }
    .leaflet-popup-tip {
        background: black;
    }
    .leaflet-tooltip {
        background-color: black;
        border-radius: 6px;
        font-weight: bold;
        color: white;
    }
    </style>
    """

    m.get_root().html.add_child(folium.Element(custom_css))

    base_url = "https://warnung.bund.de/api31/"
    for warning_provider in ["dwd", "katwarn", "mowas", "police", "lhp", "biwapp"]:
        url = f"{base_url}/{warning_provider}/mapData.json"
        response = requests.get(url)
        if response.status_code == 200:
            warnings = response.json()
            for warning in warnings:
                geojson_url = f"{base_url}/warnings/{warning['id']}.geojson"
                geojson_response = requests.get(geojson_url)

                info_url = f"{base_url}/warnings/{warning['id']}.json"
                info_response = requests.get(info_url)

                if info_response.status_code == 200:
                    info_data = info_response.json()
                    actual_info = info_data["info"][0]

                    event = actual_info["event"]
                    severity = actual_info["severity"]
                    event_code = actual_info["eventCode"][0].get("value", "Unknown Event Code")


                    # check if the id starts with dwd
                    if warning['id'].startswith("dwd"):
                        event_code_icon_url = f"{base_url}/appdata/gsb/eventCodes/BBK-EVC-062.png"
                    else:
                        event_code_icon_url = f"{base_url}/appdata/gsb/eventCodes/{event_code}.png"
                    print(f"Event Code Icon URL: {event_code_icon_url}")
                    event_code_icon = folium.CustomIcon(
                        icon_image=event_code_icon_url,
                        icon_size=(30, 30)
                    )

                    print(f"Event: {event}, Severity: {severity}, Event Code: {event_code}")


                if geojson_response.status_code == 200:
                    geojson_data = geojson_response.json()

                    feature = geojson_data['features'][0]  # or loop over them
                    properties = feature.get("properties", {})

                    html = f"""
                    <style>
                    .title {{
                        color: {properties.get('fillColor', 'white')};
                    }}
                    body {{
                        background-color: black;
                        color: white;
                    }}
                    </style>
                    <b class="title">{actual_info['headline']}</b><br><br>
                    {actual_info['description']}
                    """

                    html_tooltip = f"""
                    <style>
                    .title {{
                        color: {properties.get('fillColor', 'white')};
                    }}
                    </style>
                    <b class="title">{actual_info['headline']}</br></b>
                    <p class=""><i>{actual_info['event']}</i></p>
                    """

                    iframe = IFrame(html=html, width=300, height=300)

                    polygon = shape.Polygon([(point[0], point[1]) for point in geojson_data['features'][0]['geometry']['coordinates'][0]])
                    centroid = polygon.centroid

                    folium.Marker(
                        location=[centroid.y, centroid.x],
                        icon=event_code_icon,
                        tooltip=folium.Tooltip(html_tooltip, parse_html=True),
                        popup=folium.Popup(iframe, max_width=400)
                    ).add_to(m)

                    folium.GeoJson(
                        geojson_data,
                        style_function=lambda feature: {
                            "color": feature["properties"].get("strokeColor", "gray"),
                            "weight": feature["properties"].get("strokeWeight", 1),
                            "fillColor": feature["properties"].get("fillColor", "gray"),
                            "fillOpacity": 0.5,
                    },
                    tooltip=folium.Tooltip(html_tooltip, parse_html=True),
                    popup=folium.Popup(iframe, max_width=400)
                ).add_to(m)

        else:
            print(f"Error fetching warnings from {warning_provider}")
