"""
Plugin Loader for HttpPro.

This module provides dynamic plugin discovery and loading functionality
for the HttpPro proxy system.
"""

import importlib.util
import os
import sys
import logging
from mitmproxy import ctx

logger = logging.getLogger('httppro.loader')

def discover_plugins(plugins_dir):
    """
    Dynamically discover and load plugins from the specified directory.
    
    Args:
        plugins_dir: Directory path to search for plugins
        
    Returns:
        list: List of loaded plugin modules
    """
    # Navigate to the plugins directory
    plugins_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'plugins'))
    plugins = []
    
    if plugins_root not in sys.path:
        sys.path.insert(0, plugins_root)
        logger.debug(f"Added {plugins_root} to sys.path")

    if os.path.isdir(plugins_root):
        for filename in os.listdir(plugins_root):
            if not (filename.endswith('.py') and not filename.startswith('_')):
                continue
                
            mod_name = filename[:-3]
            spec = importlib.util.spec_from_file_location(mod_name, os.path.join(plugins_root, filename))
            
            if spec is None or spec.loader is None:
                logger.warning(f"Could not load plugin {filename}: spec or loader is None")
                continue
                
            module = importlib.util.module_from_spec(spec)

            try:
                sys.modules[mod_name] = module
                spec.loader.exec_module(module)
                
                # Check if module is disabled
                if hasattr(module, 'disabled') and getattr(module, 'disabled', False):
                    logger.info(f"Skipping disabled plugin: {mod_name}")
                    continue
                
                # Check if module has addons
                if hasattr(module, 'addons'):
                    plugins.append(module)
                    logger.info(f"Loaded plugin: {mod_name} (has addons)")
                else:
                    # Try to find classes that could be addons
                    found_addon = False
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            not attr_name.startswith('_') and 
                            hasattr(attr, '__init__')):
                            # This looks like a potential addon class
                            found_addon = True
                            break
                    
                    if found_addon:
                        plugins.append(module)
                        logger.info(f"Loaded plugin: {mod_name} (has addon classes)")
                    else:
                        logger.warning(f"Plugin {mod_name} loaded but has no addons or addon classes")
                        
            except Exception as e:
                logger.error(f"Failed to load plugin {mod_name}: {e}")
                
        loaded_names = [filename[:-3] for filename in os.listdir(plugins_root) 
                       if filename.endswith('.py') and not filename.startswith('_')]
        logger.info(f"Plugin discovery complete: {len(plugins)} loaded from {len(loaded_names)} found")
    else:
        logger.warning(f"Plugins directory does not exist: {plugins_root}")
        
    return plugins