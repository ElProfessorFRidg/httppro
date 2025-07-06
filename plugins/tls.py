"""
TLS Error Management Plugin for HttpPro.

This plugin automatically detects TLS handshake failures and adds the failing
domains to the ignore list to prevent future interception attempts.
"""

import os
import sys
import logging
from mitmproxy import ctx, tcp

# Add the core directory to sys.path to import database module
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))
from database import IgnoreHostsDB

logger = logging.getLogger('httppro.tls')

class TlsManager:
    """
    TLS Error Management Plugin.
    
    Automatically detects TLS handshake failures and manages domain ignore list
    through database storage with comprehensive tracking and statistics.
    """
    def __init__(self):
        """
        Initialize TLS Manager plugin.
        
        Sets up database connection, imports existing domains, and configures
        the mitmproxy ignore hosts option.
        """
        logger.info("Initializing TLS Manager plugin")
        
        self.db = IgnoreHostsDB()
        self.ignore_hosts_file = os.path.join(os.path.dirname(__file__), 'ignore-host.txt')
        
        # Import existing file into database if it exists
        if os.path.exists(self.ignore_hosts_file):
            imported = self.db.import_from_file(self.ignore_hosts_file, "file_import")
            if imported > 0:
                logger.info(f"Imported {imported} domains from ignore-host.txt to database")
        
        # Load ignore hosts from database
        self.ignore_hosts = set(self.db.get_active_domains())
        self.ignore_hosts.add('plugin-tls-loaded')
        self.update_ignore_hosts()
        
        logger.info(f"TLS Manager initialized with {len(self.ignore_hosts)-1} domains")

    def load_ignore_hosts(self):
        """
        Load ignore hosts from database.
        
        Returns:
            set: Set of domain names to ignore
        """
        domains = self.db.get_active_domains()
        return set(domains)

    def save_ignore_hosts(self):
        """Export current domains to file for backward compatibility."""
        domains_to_export = [domain for domain in self.ignore_hosts if domain != 'plugin-tls-loaded']
        
        try:
            with open(self.ignore_hosts_file, 'w') as file:
                for host in sorted(domains_to_export):
                    file.write(f"{host}\n")
                file.write("plugin-tls-loaded\n")
            logger.debug(f"Exported {len(domains_to_export)} domains to compatibility file")
        except Exception as e:
            logger.error(f"Failed to save compatibility file: {e}")

    def update_ignore_hosts(self):
        """
        Update mitmproxy ignore hosts configuration.
        
        Combines existing command-line ignore hosts with database domains
        and updates mitmproxy runtime configuration.
        """
        self.save_ignore_hosts()
        
        # Preserve existing ignore_hosts from command line or other sources
        existing_ignore_hosts = list(ctx.options.ignore_hosts) if ctx.options.ignore_hosts else []
        
        if self.ignore_hosts:
            # Filter out the plugin marker and convert to list for mitmproxy
            domains_to_ignore = [domain for domain in self.ignore_hosts if domain != 'plugin-tls-loaded']
            if domains_to_ignore:
                # Combine existing ignore hosts with our domains, avoiding duplicates
                combined_ignore_hosts = existing_ignore_hosts.copy()
                for domain in domains_to_ignore:
                    if domain not in combined_ignore_hosts:
                        combined_ignore_hosts.append(domain)
                
                ctx.options.ignore_hosts = combined_ignore_hosts
                logger.info(f"Combined ignore hosts: {len(existing_ignore_hosts)} existing + {len(domains_to_ignore)} from DB = {len(combined_ignore_hosts)} total")
            else:
                # Keep existing ignore hosts if we only have the plugin marker
                ctx.options.ignore_hosts = existing_ignore_hosts
                logger.info("Keeping existing ignore hosts (only plugin marker found in DB)")
        else:
            # Keep existing ignore hosts if database is empty
            ctx.options.ignore_hosts = existing_ignore_hosts
            logger.info("Keeping existing ignore hosts (ignore hosts DB is empty)")
        
        # Get and log database statistics
        stats = self.db.get_stats()
        logger.debug(f"Database statistics: {stats.get('active_domains', 0)} active domains")
        logger.debug(f"Total active ignore hosts: {len(ctx.options.ignore_hosts)}")

    def tcp_end(self, flow: tcp.TCPFlow):
        """
        Handle TCP connection end events.
        
        Detects TLS errors in TCP connections and automatically adds
        failing domains to the ignore list.
        
        Args:
            flow: TCP flow object from mitmproxy
        """
        if not flow.server_conn or not hasattr(flow.server_conn, 'ip_address') or not flow.server_conn.ip_address:
            return
            
        sni = flow.server_conn.sni
        if not sni:
            return
            
        if hasattr(flow, "error") and flow.error and "TLS" in flow.error.msg:
            if sni not in self.ignore_hosts:
                logger.info(f"TCP TLS handshake failure detected for {sni}, adding to ignore list")
                self.db.add_domain(sni, "tcp_tls_error")
                self.ignore_hosts.add(sni)
                self.update_ignore_hosts()
            return

    def tls_failed_client(self, data):
        """
        Handle TLS client failures.
        
        Detects TLS handshake failures from client side and automatically
        adds failing domains to the ignore list.
        
        Args:
            data: TLS failure data from mitmproxy
        """
        sni = getattr(data, "sni", None) or getattr(data, "server_name", None) or getattr(data, "server_hostname", None)
        
        if not sni:
            try:
                client_ctx = getattr(data, "context", None)
                if client_ctx and hasattr(client_ctx, 'server'):
                    sni = getattr(client_ctx.server, "sni", None) or \
                          (getattr(client_ctx.server, "address", [None])[0] if client_ctx.server.address else None)
            except Exception as e:
                logger.error(f"Exception while extracting SNI from context: {e}")
                
        if not sni:
            try:
                server_address = data.server_conn.address
                if server_address:
                    sni = server_address[0]
                    logger.warning(f"TLS failed, SNI not available, using server IP: {sni}")
            except Exception:
                logger.error("TLS failed but SNI/domain/IP could not be extracted")
                return
                
        if sni and sni not in self.ignore_hosts:
            logger.info(f"Client TLS handshake failure for {sni}, adding to ignore list")
            self.db.add_domain(sni, "client_tls_error")
            self.ignore_hosts.add(sni)
            self.update_ignore_hosts()

# Export addon for mitmproxy
addons = [
    TlsManager()
]
