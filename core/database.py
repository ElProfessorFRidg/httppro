"""
Database manager for HttpPro ignore hosts tracking.

This module provides SQLite database functionality for tracking ignored domains
with comprehensive metadata including origin tracking, timestamps, and statistics.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger('httppro.database')

class IgnoreHostsDB:
    """
    Database manager for ignored hosts with comprehensive tracking.
    
    Provides functionality to store, retrieve, and manage domains that should
    be ignored by the proxy, with full audit trail and statistics.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager.
        
        Args:
            db_path: Optional custom database path. If None, uses default location.
        """
        if db_path is None:
            # Place database in the same directory as this file
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ignore_hosts.db')
        
        self.db_path = db_path
        logger.info(f"Initializing database at: {self.db_path}")
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ignore_hosts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        domain TEXT UNIQUE NOT NULL,
                        origin TEXT NOT NULL,
                        date_added TEXT NOT NULL,
                        last_seen TEXT NOT NULL,
                        count INTEGER DEFAULT 1,
                        active BOOLEAN DEFAULT 1
                    )
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_domain ON ignore_hosts(domain)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_active ON ignore_hosts(active)
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def add_domain(self, domain: str, origin: str) -> bool:
        """
        Add a domain to the ignore list with origin tracking.
        
        Args:
            domain: The domain to ignore
            origin: Source of the ignore request (e.g., 'tls_error', 'manual', 'file_import')
        
        Returns:
            True if domain was added, False if it already existed
        """
        try:
            current_time = datetime.now().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Try to insert new domain
                try:
                    cursor.execute('''
                        INSERT INTO ignore_hosts (domain, origin, date_added, last_seen, count, active)
                        VALUES (?, ?, ?, ?, 1, 1)
                    ''', (domain, origin, current_time, current_time))
                    
                    conn.commit()
                    logger.debug(f"Added new domain: {domain} (origin: {origin})")
                    return True
                    
                except sqlite3.IntegrityError:
                    # Domain already exists, update it
                    cursor.execute('''
                        UPDATE ignore_hosts 
                        SET last_seen = ?, count = count + 1, active = 1
                        WHERE domain = ?
                    ''', (current_time, domain))
                    
                    conn.commit()
                    logger.debug(f"Updated existing domain: {domain}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to add domain {domain}: {e}")
            return False
    
    def get_active_domains(self) -> List[str]:
        """Get all active domains from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT domain FROM ignore_hosts 
                    WHERE active = 1 
                    ORDER BY domain
                ''')
                
                domains = [row[0] for row in cursor.fetchall()]
                logger.debug(f"Retrieved {len(domains)} active domains from database")
                return domains
                
        except Exception as e:
            logger.error(f"Failed to get active domains: {e}")
            return []
    
    def get_domain_info(self, domain: str) -> Optional[Tuple]:
        """Get detailed information about a specific domain."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT domain, origin, date_added, last_seen, count, active
                    FROM ignore_hosts 
                    WHERE domain = ?
                ''', (domain,))
                
                return cursor.fetchone()
                
        except Exception as e:
            logger.error(f"Failed to get domain info for {domain}: {e}")
            return None
    
    def get_all_domains_info(self) -> List[Tuple]:
        """Get detailed information about all domains."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT domain, origin, date_added, last_seen, count, active
                    FROM ignore_hosts 
                    ORDER BY date_added DESC
                ''')
                
                return cursor.fetchall()
                
        except Exception as e:
            logger.error(f"Failed to get all domains info: {e}")
            return []
    
    def remove_domain(self, domain: str) -> bool:
        """Mark a domain as inactive."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE ignore_hosts 
                    SET active = 0 
                    WHERE domain = ?
                ''', (domain,))
                
                conn.commit()
                if cursor.rowcount > 0:
                    logger.info(f"Deactivated domain: {domain}")
                    return True
                else:
                    logger.warning(f"Domain not found for deactivation: {domain}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to remove domain {domain}: {e}")
            return False
    
    def import_from_file(self, file_path: str, origin: str = "file_import") -> int:
        """
        Import domains from a text file.
        
        Args:
            file_path: Path to the file containing domains (one per line)
            origin: Origin to assign to imported domains
        
        Returns:
            Number of domains imported
        """
        if not os.path.exists(file_path):
            logger.warning(f"Import file not found: {file_path}")
            return 0
        
        imported_count = 0
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    domain = line.strip()
                    if domain and not domain.startswith('#') and domain != 'plugin-tls-loaded':
                        if self.add_domain(domain, origin):
                            imported_count += 1
            
            logger.info(f"Imported {imported_count} domains from {file_path}")
            return imported_count
            
        except Exception as e:
            logger.error(f"Failed to import from file {file_path}: {e}")
            return 0
    
    def export_to_file(self, file_path: str) -> bool:
        """Export active domains to a text file."""
        try:
            domains = self.get_active_domains()
            
            with open(file_path, 'w', encoding='utf-8') as file:
                for domain in domains:
                    file.write(f"{domain}\n")
                
                # Add the plugin marker
                file.write("plugin-tls-loaded\n")
            
            logger.info(f"Exported {len(domains)} domains to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export to file {file_path}: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get statistics about the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total domains
                cursor.execute('SELECT COUNT(*) FROM ignore_hosts')
                total = cursor.fetchone()[0]
                
                # Active domains
                cursor.execute('SELECT COUNT(*) FROM ignore_hosts WHERE active = 1')
                active = cursor.fetchone()[0]
                
                # Origins breakdown
                cursor.execute('''
                    SELECT origin, COUNT(*) FROM ignore_hosts 
                    WHERE active = 1 
                    GROUP BY origin
                ''')
                origins = dict(cursor.fetchall())
                
                return {
                    'total_domains': total,
                    'active_domains': active,
                    'inactive_domains': total - active,
                    'origins': origins
                }
                
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
