# HttpPro - Advanced MITM Proxy with TLS Error Management

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![mitmproxy](https://img.shields.io/badge/mitmproxy-10.0+-green.svg)](https://mitmproxy.org/)

HttpPro is an advanced HTTP/HTTPS proxy built on top of mitmproxy that automatically handles TLS errors and provides comprehensive domain management through a SQLite database.

## ✨ Features

- **Automatic TLS Error Handling**: Automatically detects and ignores domains with TLS handshake failures
- **Database-Driven Management**: SQLite database tracks all ignored domains with timestamps and origins
- **Command-Line Interface**: Comprehensive CLI for domain management and statistics
- **Backward Compatibility**: Maintains compatibility with existing ignore-host.txt files
- **Origin Tracking**: Track why each domain was added (manual, TLS error, file import, etc.)
- **Statistics & Analytics**: Detailed statistics on ignored domains and error patterns
- **Plugin Architecture**: Extensible plugin system for custom functionality

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- mitmproxy 10.0 or higher

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/httppro.git
cd httppro
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the proxy:
```bash
python start.py
```

The proxy will start on `http://localhost:8080` by default.

## 📖 Usage

### Starting the Proxy

```bash
python start.py
```

The proxy will:
- Load existing domains from `ignore-host.txt` into the database
- Start mitmproxy with automatic TLS error handling
- Preserve any command-line `--ignore-hosts` configuration

### Database Management

HttpPro includes a comprehensive CLI tool for managing ignored domains:

#### List domains
```bash
python manage_db.py list                    # Active domains only
python manage_db.py list --all             # All domains (active + inactive)
```

#### Add a domain
```bash
python manage_db.py add "example.com"                      # Origin: manual
python manage_db.py add "example.com" --origin "custom"    # Custom origin
```

#### Search for a domain
```bash
python manage_db.py search "graph.facebook.com"
```

#### View statistics
```bash
python manage_db.py stats
```

#### Import/Export domains
```bash
python manage_db.py import domains.txt --origin "bulk_import"
python manage_db.py export output.txt
```

#### Deactivate a domain
```bash
python manage_db.py remove "example.com"
```

## 🏗️ Architecture

### Project Structure

```
httppro/
├── core/
│   ├── __init__.py
│   ├── database.py          # SQLite database manager
│   ├── entry.py             # Application entry point
│   ├── loader.py            # Plugin loader
│   └── proxy.py             # Main proxy script
├── plugins/
│   ├── __init__.py
│   └── tls.py               # TLS error handling plugin
├── config/
│   └── logging.yaml         # Logging configuration
├── logs/                    # Log files directory
├── tests/                   # Unit tests
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
├── start.py                 # Main entry point
├── manage_db.py             # Database CLI tool
├── requirements.txt         # Python dependencies
├── setup.py                 # Package setup
├── .gitignore              # Git ignore file
├── .github/                # GitHub workflows
└── README.md               # This file
```

### Data Flow

1. **Startup**: Plugin imports domains from existing `ignore-host.txt` files
2. **Runtime**: TLS errors are automatically detected and added to database
3. **Persistence**: Database is continuously updated, file is kept for compatibility
4. **Management**: CLI tool provides full CRUD operations on domain database

## 🗄️ Database Schema

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

### Origin Types

- `existing_file`: Imported from existing ignore-host.txt
- `file_import`: Imported via CLI tool
- `tcp_tls_error`: TLS error detected in TCP layer
- `client_tls_error`: TLS error detected in client layer
- `manual`: Added manually via CLI
- `api`: Added via API (if implemented)

## 🔧 Configuration

### Environment Variables

- `HTTPPRO_DB_PATH`: Custom database file path
- `HTTPPRO_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `HTTPPRO_PROXY_PORT`: Proxy listening port (default: 8080)

### Logging

Logging is configured via `config/logging.yaml`. Logs are written to:
- Console (INFO level and above)
- `logs/httppro.log` (DEBUG level and above)
- `logs/errors.log` (ERROR level and above)

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

Run with coverage:
```bash
python -m pytest tests/ --cov=core --cov=plugins
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and development process.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [mitmproxy](https://mitmproxy.org/) - The core proxy engine
- [SQLite](https://sqlite.org/) - Database engine
- All contributors who helped improve this project

## 📞 Support

- Create an [issue](https://github.com/yourusername/httppro/issues) for bug reports or feature requests
- Check the [documentation](docs/) for detailed guides
- See [examples](examples/) for usage examples

---

**HttpPro** - Making HTTP/HTTPS proxy management simple and reliable.
