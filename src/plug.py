from abc import ABC, abstractmethod
from typing import Any, List, Type
import importlib.util
import os
import inspect
from pathlib import Path
import logging
from map import logger_main

logger_plug = logger_main


class CountryPlugin(ABC):
    """Base interface for country-specific plugins"""

    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def get_country_code(self) -> str:
        pass

    @abstractmethod
    def add_alerts_to_map(self, map_object: Any) -> None:
        pass

    @abstractmethod
    def refresh_alerts_on_map(self, map_object: Any) -> None:
        pass

    @abstractmethod
    def get_alerts(self) -> List[Any]:
        """Return the list of alerts"""
        pass

class PluginLoader:
    def __init__(self, plugins_directory: str = "plugins"):
        self.plugins_directory = Path(plugins_directory)
        self.loaded_plugins: List[CountryPlugin] = []

    def discover_plugins(self) -> List[Type[CountryPlugin]]:
        """Discover all plugin classes in the plugins directory"""
        plugin_classes = []
        
        if not self.plugins_directory.exists():
            logger_plug.error(f"Plugins directory '{self.plugins_directory}' does not exist")
            return plugin_classes
        
        for file_path in self.plugins_directory.glob("*.py"):
            if file_path.name.startswith("__"):
                continue
                
            try:
                spec = importlib.util.spec_from_file_location(
                    f"plugin_{file_path.stem}", file_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, CountryPlugin) and 
                        obj is not CountryPlugin):
                        plugin_classes.append(obj)
                        logger_plug.info(f"Discovered plugin: {name} in {file_path.name}")
                        
            except Exception as e:
                logger_plug.error(f"Error loading plugin from {file_path}: {e}")

        return plugin_classes

    def load_plugins(self) -> List[CountryPlugin]:
        """Load and instantiate all discovered plugins"""
        plugin_classes = self.discover_plugins()
        self.loaded_plugins = []
        
        for plugin_class in plugin_classes:
            try:
                plugin_instance = plugin_class()
                plugin_instance.initialize()
                self.loaded_plugins.append(plugin_instance)
                logger_plug.info(f"Loaded country plugin: {plugin_instance.get_country_code()}")
            except Exception as e:
                logger_plug.error(f"Error instantiating country plugin {plugin_class.__name__}: {e}")

        return self.loaded_plugins

    def get_plugin_by_country_code(self, country_code: str) -> CountryPlugin:
        """Get a specific plugin by country code"""
        for plugin in self.loaded_plugins:
            if plugin.get_country_code() == country_code:
                return plugin
        raise ValueError(f"Plugin for country code '{country_code}' not found")
    
    def list_plugins(self) -> None:
        """List all loaded plugins with their descriptions"""
        if not self.loaded_plugins:
            logger_plug.info("No country plugins loaded")
            return

        logger_plug.info("Loaded country plugins:")
        logger_plug.info("-" * 50)
        for plugin in self.loaded_plugins:
            logger_plug.info(f"ISO Country Code: {plugin.get_country_code()}")
            logger_plug.info("-" * 50)

    def add_alerts_to_map(self, map):
        for plugin in self.loaded_plugins:
            try:
                plugin.add_alerts_to_map(map)
            except Exception as e:
                logger_plug.error(f"Error adding alerts for {plugin.get_country_code()}: {e}")

    def update_countries(self, map):
        for plugin in self.loaded_plugins:
            try:
                plugin.refresh_alerts_on_map(map)
            except Exception as e:
                logger_plug.error(f"Error updating alerts for {plugin.get_country_code()}: {e}")

    def get_alerts(self) -> List[Any]:
        alerts = []
        for plugin in self.loaded_plugins:
            alerts.extend(plugin.get_alerts())
        return alerts
