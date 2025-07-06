"""
HttpPro - Advanced MITM Proxy with TLS Error Management

This package provides an advanced HTTP/HTTPS proxy built on top of mitmproxy
that automatically handles TLS errors and provides comprehensive domain
management through a SQLite database.
"""

__version__ = "1.0.0"
__author__ = "HttpPro Team"
__email__ = "contact@httppro.dev"
__license__ = "MIT"

import logging
import logging.config
import os
import yaml

# Setup logging configuration
def setup_logging():
    """Setup logging configuration from YAML file."""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'logging.yaml')
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logging.config.dictConfig(config)
        except Exception as e:
            # Fallback to basic configuration
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            logging.getLogger(__name__).warning(f"Failed to load logging config: {e}")
    else:
        # Default configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

# Get logger for this package
logger = logging.getLogger('httppro')

# Version information
VERSION_INFO = {
    'version': __version__,
    'author': __author__,
    'license': __license__
}
