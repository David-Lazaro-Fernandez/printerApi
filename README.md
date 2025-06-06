# Printer API for Boletera

A robust Python API service for managing printer operations in the Boletera system. This service handles printer status monitoring, job management, and printer configuration.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## Features
- Printer status monitoring
- Print job management
- Printer configuration
- Real-time status updates
- Error handling and logging
- RESTful API endpoints

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- A compatible printer system
- MongoDB (for data storage)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd printerApi
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```env
FLASK_APP=app
FLASK_ENV=development
PORT=5000
MONGODB_URI=your_mongodb_connection_string
PRINTER_TIMEOUT=5000
LOG_LEVEL=INFO
```

## Configuration

### Environment Variables
- `FLASK_APP`: The main application module
- `FLASK_ENV`: Environment mode (development/production)
- `PORT`: The port number where the server will run (default: 5000)
- `MONGODB_URI`: MongoDB connection string
- `PRINTER_TIMEOUT`: Timeout for printer operations in milliseconds
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Printer Configuration
1. Ensure your printer is properly connected and powered on
2. Configure printer settings in the `config/printer.py` file:
```python
PRINTER_CONFIG = {
    "name": "Your Printer Name",
    "type": "network",  # or "usb"
    "address": "192.168.1.100",  # for network printers
    "port": 9100  # default port for network printers
}
```

## Usage

1. Start the server in development mode:
```bash
flask run
```

2. Start the server in production mode:
```bash
gunicorn app:app
```

## API Endpoints

### Printer Status
- `GET /api/printer/status` - Get current printer status
- `GET /api/printer/jobs` - List all print jobs
- `POST /api/printer/print` - Send a new print job
- `DELETE /api/printer/jobs/<id>` - Cancel a print job

### Configuration
- `GET /api/printer/config` - Get printer configuration
- `PUT /api/printer/config` - Update printer configuration

## Development

### Project Structure
```
printerApi/
├── app/
│   ├── __init__.py
│   ├── controllers/
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
├── config/
├── tests/
├── requirements.txt
└── docs/
```

### Running Tests
```bash
pytest
```

### Code Style
The project follows PEP 8 style guide. Run linting:
```bash
flake8
```

### Dependencies
Key dependencies include:
- Flask: Web framework
- PyMongo: MongoDB driver
- python-escpos: Printer communication
- python-dotenv: Environment configuration
- pytest: Testing framework

## Troubleshooting

### Common Issues

1. Printer Not Responding
   - Check printer power and connection
   - Verify network connectivity
   - Check printer configuration

2. Print Jobs Not Processing
   - Verify printer status
   - Check job queue
   - Review error logs

3. Connection Issues
   - Verify MongoDB connection
   - Check network settings
   - Review firewall configuration

### Logs
Logs are stored in the `logs` directory. Check the following files for issues:
- `error.log` - Error messages
- `app.log` - Application logs
- `access.log` - API access logs

## Support

For support, please:
1. Check the troubleshooting guide
2. Review the documentation
3. Open an issue in the repository
4. Contact the development team

## License

This project is licensed under the MIT License - see the LICENSE file for details.
