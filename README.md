# 🏠 Campus Manager

**A modern student campus distribution management system built with FastAPI and Google Sheets integration.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.118+-green.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Overview

Campus Manager is an intelligent system for automating student housing distribution based on multiple criteria including academic priority, special needs, distance from campus, and family status. The system provides a fair, transparent, and data-driven approach to campus accommodation assignments.

## ✨ Features

- **🎯 Smart Distribution Algorithm** - Multi-criteria scoring system with priority handling
- **📊 Google Sheets Integration** - Seamless data management and storage
- **🔧 RESTful API** - Clean, well-documented API endpoints
- **🎨 Modern Web Interface** - Responsive frontend with real-time feedback
- **📝 Comprehensive Logging** - Detailed audit trails and error tracking
- **⚡ High Performance** - Asynchronous operations with FastAPI
- **🛡️ Type Safety** - Full Pydantic validation and type hints
- **🧪 Testable Architecture** - Clean separation of concerns

## 🏗️ Architecture

```
campus-manager/
├── 📁 core/                  # Core application components
│   ├── config.py            # Configuration management
│   ├── db.py                # Database setup
│   ├── exceptions.py        # Custom exception classes
│   ├── logging.py           # Logging configuration
│   └── lifespan.py          # Application lifecycle
├── 📁 di/                   # Dependency injection
├── 📁 domain/               # Domain models and business logic
│   ├── student.py           # Student domain model
│   └── distribution.py      # Distribution models
├── 📁 repositories/         # Data access layer
├── 📁 services/             # Business logic services
├── 📁 handlers/             # API route handlers
├── 📁 static/               # Frontend assets
├── main.py                  # Application entry point
└── requirements.txt         # Dependencies
```

### Design Principles

- **Clean Architecture** - Separation of concerns with proper abstraction layers
- **Dependency Injection** - Loose coupling and easy testing
- **SOLID Principles** - Maintainable and extensible code
- **Type Safety** - Comprehensive type hints and validation
- **Async/Await** - Non-blocking operations for better performance

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Cloud account with access to Google Sheets API
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/campus-manager.git
   cd campus-manager
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Google Sheets**
   - Follow [Google Setup Guide](GOOGLE_SETUP.md)
   - Create service account and download JSON key
   - Share your Google Sheet with the service account

5. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Running the Application

```bash
python run.py
```

The application will be available at:
- 🌐 **Frontend**: http://localhost:8000
- 📚 **API Documentation**: http://localhost:8000/docs
- 🔍 **Health Check**: http://localhost:8000/health

## 📊 Google Sheets Setup

### Required Sheets Structure

**Sheet 1: Students Data**
```
ФИО | Пол | Институт | СВО | ЧАЭС | Инвалидность | Курение | Расстояние | Многодетная семья
Иванов | М | ИПМКН | 0 | 0 | 0 | 0 | 50 | 1
Петров | М | Другое | 0 | 0 | 0 | 1 | 25 | 0
```

**Sheet 2: Institute Weights**
```
Институт | Баллы за институт | СВО | ЧАЭС | Инвалидность | Расстояние | Многодетная семья
ИПМКН | 100 | 100 | 100 | 100 | 100 | 100
Горный | 100 | 100 | 100 | 100 | 100 | 100
Другой | 50 | 100 | 100 | 100 | 100 | 100
```

**Sheet 3: Results** (auto-generated)

## 🎯 Distribution Algorithm

The system uses a comprehensive scoring algorithm:

### 1. **Data Normalization**
- Distance: `distance / 500` (normalized to 0-1 scale)
- Binary criteria: 0 or 1 (SVO, ChAES, Disability, etc.)

### 2. **Score Calculation**
```
Total Score = Institute Score +
              (SVO × SVO Weight) +
              (ChAES × ChAES Weight) +
              (Disability × Disability Weight) +
              (Smoking × Smoking Weight) +
              (Normalized Distance × Distance Weight) +
              (Large Family × Large Family Weight)
```

### 3. **Priority Ranking**
1. **Priority Students** (SVO/ChAES/Disability ≠ 0)
2. **Regular Students**
3. Within each group: sorted by total score (descending)

## 🛠️ Configuration

### Environment Variables

```bash
# Google Sheets Configuration
GOOGLE_SERVICE_ACCOUNT=service_account.json
GOOGLE_SHEET_ID=your_google_sheet_id

# Database
DB_CONNECTION_URL=sqlite:///database.db

# Application Settings
APP_NAME="Campus Manager"
VERSION="1.0.0"
DEBUG=false

# Sheet Indices
STUDENTS_SHEET_INDEX=0
WEIGHTS_SHEET_INDEX=1
RESULTS_SHEET_INDEX=2
```

## 📚 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Frontend application |
| GET | `/health` | Health check |
| GET | `/api/v1/students` | Get all students |
| POST | `/api/v1/calculate` | Calculate distribution |

### Calculate Distribution

```bash
curl -X POST "http://localhost:8000/api/v1/calculate" \
     -H "Content-Type: application/json"
```

**Response:**
```json
{
  "success": true,
  "message": "Distribution calculated for 15 students",
  "students_count": 15
}
```

## 🔧 Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Quality

```bash
# Code formatting
black .

# Type checking
mypy .

# Linting
flake8
```

### Project Structure

- **`core/`** - Essential application infrastructure
- **`domain/`** - Business entities and logic
- **`repositories/`** - Data access abstraction
- **`services/`** - Business logic implementation
- **`handlers/`** - HTTP request/response handling
- **`di/`** - Dependency injection setup

## 📈 Monitoring & Logging

The application includes comprehensive logging:

- **Colored console output** with different log levels
- **Structured logging** for easy parsing
- **Detailed error tracking** with context
- **Performance metrics** for distribution calculations

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## 🔒 Security

- **Service Account Authentication** for Google Sheets
- **Input Validation** with Pydantic models
- **Error Handling** without sensitive information exposure
- **Secure Configuration** with environment variables

## 🐛 Troubleshooting

### Common Issues

1. **Google Sheets Connection Error**
   - Verify service account file path
   - Check Google Sheet sharing permissions
   - Confirm Google Sheets API is enabled

2. **Module Import Errors**
   - Ensure running from project root
   - Check virtual environment activation
   - Verify all dependencies installed

3. **Data Validation Errors**
   - Check Google Sheets column headers
   - Verify data types and formats
   - Review log messages for specific errors

### Debug Mode

Enable debug logging by setting `DEBUG=true` in `.env` file.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add type hints to all functions
- Write comprehensive docstrings
- Include unit tests for new features
- Maintain backward compatibility

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** - Modern web framework for building APIs
- **Google Sheets API** - Data storage and management
- **Pydantic** - Data validation using Python type annotations
- **SQLModel** - SQL databases in Python

## 📞 Support

For support and questions:

- 📧 Email: support@campus-manager.dev
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/campus-manager/issues)
- 📖 Documentation: [Wiki](https://github.com/your-username/campus-manager/wiki)

---

**Built with ❤️ for educational institutions**