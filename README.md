# Shopify Mind AI

An AI-powered application built with Flutter and FastAPI that helps with Shopify store management and intelligence.

## Project Structure

```
shopify_mind_ai/
├── backend/          # FastAPI backend server
│   ├── app/
│   ├── migrations/   # Database migrations
│   └── requirements.txt
├── flutter_app/      # Flutter mobile application
├── docs/             # Documentation
└── README.md
```

## Features

- AI-powered insights for Shopify stores
- Real-time analytics and monitoring
- Cross-platform mobile application (iOS, Android, Web)
- RESTful API backend

## Getting Started

### Backend Setup

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:
   ```bash
   python -m app.main
   ```

### Flutter App Setup

1. Navigate to the flutter_app directory:

   ```bash
   cd flutter_app
   ```

2. Get dependencies:

   ```bash
   flutter pub get
   ```

3. Run the application:
   ```bash
   flutter run
   ```

## Prerequisites

- Python 3.8+ (for backend)
- Flutter 3.0+ (for mobile app)
- Dart 3.0+

## Architecture

See [Architecture Documentation](docs/architecture.md) for detailed system design and architecture decisions.

## Development

### Backend

- Framework: FastAPI
- Database: (configured in `backend/app/database.py`)
- Location: `backend/app/`

### Frontend

- Framework: Flutter
- Location: `flutter_app/`

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

(Add your license information here)

## Contact

(Add contact information here)
