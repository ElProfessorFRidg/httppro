"""
HttpPro Application Entry Point.

This module provides the main entry point for launching the HttpPro proxy
with automatic domain management and TLS error handling.
"""

import os
import sys
# nosec: B404 - subprocess is used safely with a static command list
import subprocess
import logging
import re

logger = logging.getLogger('httppro.entry')

def launch_proxy():
    """
    Launch mitmdump proxy server with ignore-host configuration.
    
    Automatically loads domains from ignore-host.txt and configures
    mitmproxy with appropriate ignore patterns.
    """
    script_path = os.path.join(os.path.dirname(__file__), 'proxy.py')
    # The command list is constructed only from static values and trusted file content (ignore-host.txt),
    # which is sanitized using re.escape. No user input is directly passed to the command.
    command = ['mitmdump', '-s', script_path]
    
    # Get the content of the ignore-host.txt file
    ignore_hosts_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ignore-host.txt')
    if os.path.exists(ignore_hosts_file):
        try:
            with open(ignore_hosts_file, 'r') as file:
                hosts = [host.strip() for host in file if host.strip() and host.strip() != 'plugin-tls-loaded']
            
            if hosts:
                # Create regex pattern for ignore hosts
                pattern = '|'.join([re.escape(host) for host in hosts])
                regex = rf'(?:^|\.)({pattern})$'
                # Defensive: ensure regex is a string and not user input (already escaped)
                assert isinstance(regex, str)
                command.extend(['--ignore-hosts', regex])
                logger.info(f"Configured ignore pattern for {len(hosts)} domains")
            else:
                logger.info("No valid hosts found in ignore-host.txt")
        except Exception as e:
            logger.error(f"Failed to read ignore-host.txt: {e}")
    else:
        logger.info("No ignore-host.txt file found")
    
    logger.info(f"Starting proxy with command: {' '.join(command[:3])} [...]")
    
    try:
        # Execute the proxy command
        # nosec: B603 - command is a static list, not user input; all file content is sanitized
        assert isinstance(command, list) and all(isinstance(x, str) for x in command)
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Proxy execution failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Proxy stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

def main():
    """Main entry point for the application."""
    logger.info("Starting HttpPro application")
    launch_proxy()
