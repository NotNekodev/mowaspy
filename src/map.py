import folium
from plug import PluginLoader

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

    def iterate_over_countries(self):
        """Iterate over all loaded plugins and add their alerts to the map"""
        for plugin in self.plugman.loaded_plugins:
            try:
                plugin.add_alerts_to_map(self.map)
            except Exception as e:
                print(f"Error adding alerts for {plugin.get_country_code()}: {e}")

    def add_layer(self, layer):
        layer.add_to(self.map)

    def render(self):
        return self.map._repr_html_()
