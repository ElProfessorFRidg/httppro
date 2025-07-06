#!/usr/bin/env python3
"""
HttpPro - Advanced MITM Proxy with TLS Error Management

Main entry point for the HttpPro application.
"""

import os
import sys
import logging

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup logging before importing other modules
try:
    from __init__ import setup_logging, VERSION_INFO
    setup_logging()
except ImportError:
    # Fallback logging setup
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    VERSION_INFO = {'version': '1.0.0', 'license': 'MIT', 'author': 'HttpPro Team'}

from core.entry import main

logger = logging.getLogger('httppro.main')

def display_banner():
    """Display application banner."""
    banner = f"""
╔═══════════════════════════════════════════════════════════════╗
║                          HttpPro v{VERSION_INFO['version']:<6}                        ║
║            Advanced MITM Proxy with TLS Error Management     ║
║                                                               ║
║  • Automatic TLS error handling                              ║
║  • Database-driven domain management                         ║
║  • Comprehensive logging and statistics                      ║
║                                                               ║
║  License: {VERSION_INFO['license']:<10} | Author: {VERSION_INFO['author']:<20}   ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)

if __name__ == "__main__":
    try:
        display_banner()
        logger.info("Starting HttpPro application")
        main()
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        sys.exit(1)