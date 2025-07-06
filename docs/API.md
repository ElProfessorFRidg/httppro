# HttpPro API Documentation

## Database API

### IgnoreHostsDB Class

The `IgnoreHostsDB` class provides comprehensive database management for ignored domains.

#### Constructor

```python
db = IgnoreHostsDB(db_path=None)
```

**Parameters:**
- `db_path` (Optional[str]): Custom database file path. If None, uses default location.

#### Methods

##### add_domain(domain, origin)

Add a domain to the ignore list.

```python
success = db.add_domain("example.com", "manual")
```

**Parameters:**
- `domain` (str): Domain name to add
- `origin` (str): Origin of the domain (e.g., "manual", "tls_error", "file_import")

**Returns:**
- `bool`: True if domain was newly added, False if it already existed (but was updated)

##### get_active_domains()

Get all active domains from the database.

```python
domains = db.get_active_domains()
```

**Returns:**
- `List[str]`: List of active domain names

##### get_domain_info(domain)

Get detailed information about a specific domain.

```python
info = db.get_domain_info("example.com")
```

**Parameters:**
- `domain` (str): Domain name to look up

**Returns:**
- `Optional[Tuple]`: (domain, origin, date_added, last_seen, count, active) or None if not found

##### remove_domain(domain)

Deactivate a domain (mark as inactive).

```python
success = db.remove_domain("example.com")
```

**Parameters:**
- `domain` (str): Domain name to deactivate

**Returns:**
- `bool`: True if domain was found and deactivated, False otherwise

##### get_stats()

Get database statistics.

```python
stats = db.get_stats()
```

**Returns:**
- `dict`: Statistics including total_domains, active_domains, inactive_domains, and origins breakdown

##### import_from_file(file_path, origin)

Import domains from a text file.

```python
count = db.import_from_file("domains.txt", "bulk_import")
```

**Parameters:**
- `file_path` (str): Path to file containing domains (one per line)
- `origin` (str): Origin to assign to imported domains

**Returns:**
- `int`: Number of domains successfully imported

##### export_to_file(file_path)

Export active domains to a text file.

```python
success = db.export_to_file("output.txt")
```

**Parameters:**
- `file_path` (str): Path where to write the domains

**Returns:**
- `bool`: True if export was successful, False otherwise

## Plugin API

### TlsManager Class

The `TlsManager` class is a mitmproxy addon that automatically handles TLS errors.

#### Methods

##### tcp_end(flow)

Handle TCP connection end events to detect TLS errors.

```python
def tcp_end(self, flow: tcp.TCPFlow):
    # Automatically called by mitmproxy
```

##### tls_failed_client(data)

Handle TLS client failures.

```python
def tls_failed_client(self, data):
    # Automatically called by mitmproxy
```

## CLI Tool API

The `manage_db.py` tool provides command-line access to database operations.

### Commands

#### list

List domains from the database.

```bash
python manage_db.py list [--all]
```

Options:
- `--all`: Include inactive domains

#### add

Add a domain to the database.

```bash
python manage_db.py add "example.com" [--origin "manual"]
```

Options:
- `--origin`: Origin tag for the domain (default: "manual")

#### remove

Deactivate a domain.

```bash
python manage_db.py remove "example.com"
```

#### search

Search for domain information.

```bash
python manage_db.py search "example.com"
```

#### stats

Show database statistics.

```bash
python manage_db.py stats
```

#### import

Import domains from a file.

```bash
python manage_db.py import "domains.txt" [--origin "file_import"]
```

Options:
- `--origin`: Origin tag for imported domains (default: "file_import")

#### export

Export domains to a file.

```bash
python manage_db.py export "output.txt"
```

## Configuration

### Environment Variables

- `HTTPPRO_DB_PATH`: Custom database file path
- `HTTPPRO_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `HTTPPRO_PROXY_PORT`: Proxy listening port (default: 8080)

### Logging Configuration

Logging is configured via `config/logging.yaml`. Key loggers:

- `httppro`: Main application logger
- `httppro.database`: Database operations
- `httppro.tls`: TLS plugin operations
- `mitmproxy`: mitmproxy framework logs

## Origin Types

The system tracks the origin of each ignored domain:

- `existing_file`: Imported from existing ignore-host.txt
- `file_import`: Imported via CLI import command
- `tcp_tls_error`: TLS error detected in TCP layer
- `client_tls_error`: TLS error detected in client layer
- `manual`: Added manually via CLI
- `migration`: Added during migration from old format
- `api`: Added programmatically via API

## Database Schema

```sql
CREATE TABLE ignore_hosts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT UNIQUE NOT NULL,
    origin TEXT NOT NULL,
    date_added TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    count INTEGER DEFAULT 1,
    active BOOLEAN DEFAULT 1
);
```

## Error Handling

All API methods include comprehensive error handling and logging. Database operations are atomic and use transactions for consistency.

## Thread Safety

The database operations are designed to be thread-safe through SQLite's built-in locking mechanisms.
