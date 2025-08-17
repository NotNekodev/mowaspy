import folium
from plug import PluginLoader
from typing import List
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s[%(levelname)s]: %(message)s')

logger_main = logging.getLogger("nocto-core")

class NoctoMap:
    def __init__(self):
        self.map = folium.Map(location=[51.0, 10.0], zoom_start=6)
        with open("src/frontend/global.css") as f:
            self.css = f.read()
        self.map.get_root().html.add_child(folium.Element(f"<style>{self.css}</style>"))
        self.plugman = PluginLoader(plugins_directory="src/api")
        self.plugman.discover_plugins()
        self.plugman.load_plugins()
        self.plugman.list_plugins()

        for plugin in self.plugman.loaded_plugins:
            try:
                plugin.add_alerts_to_map(self.map)
            except Exception as e:
                logger_main.error(f"Error adding alerts for {plugin.get_country_code()}: {e}")
        

    def update(self):
        """Update the map with the latest alerts from all plugins"""
        for plugin in self.plugman.loaded_plugins:
            try:
                plugin.refresh_alerts_on_map(self.map)
            except Exception as e:
                logger_main.error(f"Error updating alerts for {plugin.get_country_code()}: {e}")

    def get_alerts(self):
        """Get the current alerts from all plugins"""
        return self.plugman.get_alerts()
