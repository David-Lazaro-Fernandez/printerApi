# Printer API for Boletera

A robust API service for managing printer operations in the Boletera system. This service handles printer status monitoring, job management, and printer configuration.

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
- Node.js (v14 or higher)
- npm (v6 or higher)
- A compatible printer system
- MongoDB (for data storage)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd printerApi
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file in the root directory with the following variables:
```env
PORT=3000
MONGODB_URI=your_mongodb_connection_string
PRINTER_TIMEOUT=5000
LOG_LEVEL=info
```

## Configuration

### Environment Variables
- `PORT`: The port number where the server will run (default: 3000)
- `MONGODB_URI`: MongoDB connection string
- `PRINTER_TIMEOUT`: Timeout for printer operations in milliseconds
- `LOG_LEVEL`: Logging level (debug, info, warn, error)

### Printer Configuration
1. Ensure your printer is properly connected and powered on
2. Configure printer settings in the `config/printer.js` file:
```javascript
{
  name: "Your Printer Name",
  type: "network", // or "usb"
  address: "192.168.1.100", // for network printers
  port: 9100 // default port for network printers
}
```

## Usage

1. Start the server:
```bash
npm start
```

2. For development:
```bash
npm run dev
```

3. For production:
```bash
npm run prod
```

## API Endpoints

### Printer Status
- `GET /api/printer/status` - Get current printer status
- `GET /api/printer/jobs` - List all print jobs
- `POST /api/printer/print` - Send a new print job
- `DELETE /api/printer/jobs/:id` - Cancel a print job

### Configuration
- `GET /api/printer/config` - Get printer configuration
- `PUT /api/printer/config` - Update printer configuration

## Development

### Project Structure
```
printerApi/
├── src/
│   ├── controllers/
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
├── config/
├── tests/
└── docs/
```

### Running Tests
```bash
npm test
```

### Code Style
The project follows ESLint configuration. Run linting:
```bash
npm run lint
```

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
- `combined.log` - All logs
- `access.log` - API access logs

## Support

For support, please:
1. Check the troubleshooting guide
2. Review the documentation
3. Open an issue in the repository
4. Contact the development team

## License

This project is licensed under the MIT License - see the LICENSE file for details.
