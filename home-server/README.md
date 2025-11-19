# IoT Monitoring System - Home Server

Backend server for IoT sensor monitoring and data visualization.

## Project Structure
```
home-server/
├── app/              # Core application modules
├── services/         # Long-running services
├── web/             # Web interface files
├── tests/           # Test scripts
├── scripts/         # Utility scripts
├── data/            # Data storage
└── logs/            # Log files
```

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Mosquitto MQTT broker

### Installation
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
psql -U postgres -f scripts/setup_database.sql
```

## Usage

### Start MQTT Listener
```bash
python run.py listener
```

### Start Web Server
```bash
python run.py web
```

Then open: http://localhost:5000

### Run Tests
```bash
python run.py test
```

## Configuration

Edit `config.py` to change settings:
- MQTT broker connection
- Database credentials
- Web server port
- Data retention periods

## Development

### Running in VS Code

1. Open folder in VS Code
2. Select Python interpreter: `venv/bin/python`
3. Set breakpoints
4. Press F5 to debug

### Project Components

- **app/database.py** - Database operations
- **services/mqtt_listener.py** - MQTT message handler
- **services/web_server.py** - Web dashboard
- **web/templates/** - HTML templates
- **web/static/** - CSS, JavaScript

## License

Private project
```

---

## Final Structure View
```
~/iot-remote/
│
├── home-server/              # Backend (organized!)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── database.py       ✅ Core database module
│   │   └── utils.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── mqtt_listener.py  ✅ MQTT service
│   │   └── web_server.py     ⏳ Next to create
│   ├── web/
│   │   ├── templates/
│   │   └── static/
│   ├── tests/
│   ├── scripts/
│   ├── data/
│   ├── logs/
│   ├── venv/
│   ├── config.py
│   ├── run.py                ✅ Main entry point
│   ├── requirements.txt
│   └── README.md
│
└── mock-data/                # Client (already organized)
    ├── config.py
    ├── mock_generator.py
    ├── venv/
    └── requirements.txt
