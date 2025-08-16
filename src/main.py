import folium
import os
import webview

from de.de import add_de_warnings

m = folium.Map(location=[51.0, 10.0], zoom_start=6)

add_de_warnings(m)

m.save("map.html")

# Display in a webview window
webview.create_window("MoWaSpy Alerts", os.path.join(os.getcwd(), "map.html"))
webview.start()