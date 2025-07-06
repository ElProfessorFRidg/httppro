"""
HttpPro Main Proxy Script.

This module serves as the main entry point for mitmproxy and handles
plugin loading and addon registration.
"""

import sys 
import os
import logging

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.loader import discover_plugins

logger = logging.getLogger('httppro.proxy')

# Plugin discovery
PLUGINS_DIR = os.path.join(os.path.dirname(__file__), 'plugins')
plugins = discover_plugins(PLUGINS_DIR)

# Collect all addons from loaded plugins
addons = []
for plugin in plugins:
    if hasattr(plugin, 'addons'):
        if isinstance(plugin.addons, list):
            addons.extend(plugin.addons)
        else:
            addons.append(plugin.addons)
    else:
        # If no addons attribute, try to find classes that could be addons
        for attr_name in dir(plugin):
            attr = getattr(plugin, attr_name)
            if (isinstance(attr, type) and 
                not attr_name.startswith('_') and 
                hasattr(attr, '__init__')):
                try:
                    # Try to instantiate the class
                    instance = attr()
                    addons.append(instance)
                    logger.info(f"Auto-loaded addon class: {attr_name} from {plugin.__name__}")
                    break  # Only take the first valid class per plugin
                except Exception as e:
                    logger.warning(f"Could not instantiate {attr_name}: {e}")

logger.info(f"Proxy initialized with {len(addons)} addons")
for i, addon in enumerate(addons):
    logger.debug(f"  {i+1}. {addon.__class__.__name__} from {addon.__class__.__module__}")