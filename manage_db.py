#!/usr/bin/env python3
"""
HttpPro Database Management CLI.

Command-line utility for managing the HttpPro ignore hosts database.
Provides comprehensive CRUD operations and statistics.
"""

import sys
import os
import argparse
import logging
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add the core directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

try:
    from core.database import IgnoreHostsDB
except ImportError:
    print("Error: Could not import database module. Make sure you're running from the correct directory.")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and errors by default
    format='%(levelname)s: %(message)s'
)

def list_domains(db: IgnoreHostsDB, show_inactive: bool = False):
    """List all domains with their information."""
    domains = db.get_all_domains_info()
    
    if not domains:
        print("No domains found in database.")
        return
    
    active_count = sum(1 for _, _, _, _, _, active in domains if active)
    total_count = len(domains)
    
    print(f"Found {total_count} domains in database ({active_count} active, {total_count - active_count} inactive)\n")
    print(f"{'Domain':<40} {'Origin':<20} {'Added':<20} {'Count':<6} {'Status'}")
    print("-" * 95)
    
    for domain, origin, date_added, last_seen, count, active in domains:
        if not show_inactive and not active:
            continue
            
        status = "Active" if active else "Inactive"
        date_str = datetime.fromisoformat(date_added).strftime("%Y-%m-%d %H:%M")
        print(f"{domain:<40} {origin:<20} {date_str:<20} {count:<6} {status}")

def add_domain(db: IgnoreHostsDB, domain: str, origin: str = "manual"):
    """Add a domain to the database."""
    if db.add_domain(domain, origin):
        print(f"Added domain: {domain}")
    else:
        print(f"Domain already exists (updated): {domain}")

def remove_domain(db: IgnoreHostsDB, domain: str):
    """Remove (deactivate) a domain from the database."""
    if db.remove_domain(domain):
        print(f"Deactivated domain: {domain}")
    else:
        print(f"Domain not found: {domain}")

def show_stats(db: IgnoreHostsDB):
    """Show database statistics."""
    stats = db.get_stats()
    
    print("Database Statistics:")
    print(f"   Total domains: {stats.get('total_domains', 0)}")
    print(f"   Active domains: {stats.get('active_domains', 0)}")
    print(f"   Inactive domains: {stats.get('inactive_domains', 0)}")
    
    origins = stats.get('origins', {})
    if origins:
        print("\nDomains by origin:")
        for origin, count in sorted(origins.items()):
            print(f"   {origin}: {count}")

def import_file(db: IgnoreHostsDB, file_path: str, origin: str = "file_import"):
    """Import domains from a file."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    count = db.import_from_file(file_path, origin)
    print(f"Imported {count} domains from {file_path}")

def export_file(db: IgnoreHostsDB, file_path: str):
    """Export active domains to a file."""
    if db.export_to_file(file_path):
        print(f"Exported domains to {file_path}")
    else:
        print(f"Failed to export to {file_path}")

def search_domain(db: IgnoreHostsDB, domain: str):
    """Search for a specific domain."""
    info = db.get_domain_info(domain)
    
    if info:
        domain, origin, date_added, last_seen, count, active = info
        status = "Active" if active else "Inactive"
        date_added_str = datetime.fromisoformat(date_added).strftime("%Y-%m-%d %H:%M:%S")
        last_seen_str = datetime.fromisoformat(last_seen).strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"Domain Information:")
        print(f"   Domain: {domain}")
        print(f"   Origin: {origin}")
        print(f"   Status: {status}")
        print(f"   Date Added: {date_added_str}")
        print(f"   Last Seen: {last_seen_str}")
        print(f"   Count: {count}")
    else:
        print(f"Domain not found: {domain}")

def main():
    parser = argparse.ArgumentParser(description="Manage ignore hosts database")
    parser.add_argument("--db", help="Database file path (optional)")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List domains")
    list_parser.add_argument("--all", action="store_true", help="Show inactive domains too")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a domain")
    add_parser.add_argument("domain", help="Domain to add")
    add_parser.add_argument("--origin", default="manual", help="Origin of the domain")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove (deactivate) a domain")
    remove_parser.add_argument("domain", help="Domain to remove")
    
    # Stats command
    subparsers.add_parser("stats", help="Show database statistics")
    
    # Import command
    import_parser = subparsers.add_parser("import", help="Import domains from file")
    import_parser.add_argument("file", help="File to import from")
    import_parser.add_argument("--origin", default="file_import", help="Origin to assign to imported domains")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export domains to file")
    export_parser.add_argument("file", help="File to export to")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for a domain")
    search_parser.add_argument("domain", help="Domain to search for")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize database
    try:
        db = IgnoreHostsDB(args.db)
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == "list":
            list_domains(db, args.all)
        elif args.command == "add":
            add_domain(db, args.domain, args.origin)
        elif args.command == "remove":
            remove_domain(db, args.domain)
        elif args.command == "stats":
            show_stats(db)
        elif args.command == "import":
            import_file(db, args.file, args.origin)
        elif args.command == "export":
            export_file(db, args.file)
        elif args.command == "search":
            search_domain(db, args.domain)
    except Exception as e:
        print(f"Error executing command: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
