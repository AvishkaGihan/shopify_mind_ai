# ShopifyMind AI - Decision Architecture Document

**Project:** ShopifyMind AI (Mobile App - iOS + Android)
**Author:** Winston (Architect Agent)
**Date:** November 15, 2025
**Status:** Complete & Ready for Implementation
**Version:** 1.0

---

## Executive Summary

ShopifyMind AI is a portfolio-grade mobile application (Flutter) paired with a FastAPI backend and Supabase PostgreSQL database. The architecture prioritizes **clean, scalable patterns** while maintaining **rapid development** for the 4-day MVP delivery.

**Core Philosophy:** Use boring, proven technology that works. Let proven libraries and frameworks handle complexity. Focus on perfect feature execution, not architectural innovation.

---

## Project Initialization

**First implementation story should execute these commands:**

```bash
# Create Flutter project
flutter create shopify_mind_ai --org com.shopifymind

# Add required Flutter dependencies
cd shopify_mind_ai
flutter pub add \
  get \
  http \
  hive \
  hive_flutter \
  flutter_secure_storage \
  cached_network_image \
  fl_chart \
  supabase \
  intl \
  lottie

# Initialize backend (Python/FastAPI)
cd ../backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Create Supabase project at https://supabase.com
# Run database migrations (see migrations/ folder)
```

**Starter provides these architectural decisions:**

- ✓ Language: Dart (Flutter) + Python (FastAPI)
- ✓ UI Framework: Material Design 3 (Flutter)
- ✓ State Management: GetX (reactive, lightweight)
- ✓ HTTP Client: GetX + http package
- ✓ Local Storage: Hive (fast, key-value)
- ✓ Secure Storage: flutter_secure_storage (encrypted tokens)
- ✓ Build Tooling: Gradle (Android), Xcode (iOS)
- ✓ Testing: Flutter test (built-in)
- ✓ Backend Framework: FastAPI (auto-docs, validation)
- ✓ Database: Supabase PostgreSQL (row-level security)

---

## Decision Summary Table

| #   | Category          | Decision                         | Version | Verified | Affects Epics | Rationale                                               |
| --- | ----------------- | -------------------------------- | ------- | -------- | ------------- | ------------------------------------------------------- |
| 1   | Backend Framework | FastAPI (Python)                 | 0.104+  | Nov 2025 | 1,2,3,4,5     | Fast development, built-in validation, clear structure  |
| 2   | Database          | Supabase PostgreSQL              | Latest  | Nov 2025 | All           | Row-level security, built-in auth, free tier sufficient |
| 3   | API Design        | REST with standard structure     | -       | Nov 2025 | All           | Predictable, consistent, developer-friendly             |
| 4   | Authentication    | JWT + Supabase Auth              | -       | Nov 2025 | 1             | Stateless, scalable, mobile-friendly, secure            |
| 5   | State Management  | GetX                             | 4.6+    | Nov 2025 | All           | Reactive, minimal boilerplate, fast development         |
| 6   | Local Storage     | Hive + flutter_secure_storage    | Latest  | Nov 2025 | 3,6,7         | Fast, lightweight, works with GetX, offline support     |
| 7   | Error Handling    | User-friendly messages + logging | -       | Nov 2025 | All           | Better UX, easier debugging                             |
| 8   | Animations        | Hybrid (native Flutter + Lottie) | -       | Nov 2025 | 6             | Balance of quality and development speed                |
| 9   | Response Format   | Standardized JSON structure      | -       | Nov 2025 | All           | Predictable, consistent, debuggable                     |
| 10  | Date/Time         | ISO 8601 UTC everywhere          | -       | Nov 2025 | 3,4,5         | No ambiguity, timezone-safe                             |
| 11  | Error Messages    | Friendly, helpful tone           | -       | Nov 2025 | All           | Aligns with brand, better UX                            |
| 12  | Project Structure | Flutter + FastAPI + Supabase     | -       | Nov 2025 | All           | Clear separation, scalable, organized                   |

---

## Complete Project Structure

```
shopify_mind_ai/
├── flutter_app/
│   ├── lib/
│   │   ├── main.dart
│   │   ├── config/
│   │   │   ├── theme.dart           # Emerald color system, typography
│   │   │   ├── constants.dart       # API URLs, error codes, timeouts
│   │   │   └── routes.dart          # Named navigation routes
│   │   ├── controllers/             # GetX controllers (business logic + state)
│   │   │   ├── auth_controller.dart
│   │   │   ├── chat_controller.dart
│   │   │   ├── product_controller.dart
│   │   │   ├── order_controller.dart
│   │   │   └── analytics_controller.dart
│   │   ├── services/
│   │   │   ├── api_service.dart     # Centralized HTTP client
│   │   │   ├── storage_service.dart # Hive wrapper
│   │   │   ├── auth_service.dart    # Token management
│   │   │   ├── gemini_service.dart  # Google Gemini integration
│   │   │   └── logger_service.dart
│   │   ├── models/
│   │   │   ├── user.dart
│   │   │   ├── product.dart
│   │   │   ├── conversation.dart
│   │   │   ├── order.dart
│   │   │   ├── order_item.dart
│   │   │   └── analytics_event.dart
│   │   ├── pages/
│   │   │   ├── auth/
│   │   │   │   ├── login_page.dart
│   │   │   │   ├── signup_page.dart
│   │   │   │   └── reset_password_page.dart
│   │   │   ├── customer/
│   │   │   │   ├── chat_page.dart
│   │   │   │   ├── order_page.dart
│   │   │   │   └── settings_page.dart
│   │   │   └── owner/
│   │   │       ├── dashboard_page.dart
│   │   │       ├── products_page.dart
│   │   │       ├── analytics_page.dart
│   │   │       └── settings_page.dart
│   │   └── widgets/
│   │       ├── chat_bubble.dart
│   │       ├── product_card.dart
│   │       ├── order_status_card.dart
│   │       ├── order_timeline.dart
│   │       ├── typing_indicator.dart
│   │       ├── metric_card.dart
│   │       ├── error_dialog.dart
│   │       └── shared_widgets.dart
│   ├── assets/
│   │   ├── animations/              # Lottie JSON files
│   │   │   ├── typing_indicator.json
│   │   │   ├── empty_state.json
│   │   │   └── loading.json
│   │   ├── images/
│   │   │   ├── placeholder.png
│   │   │   └── logo.png
│   │   └── fonts/
│   ├── pubspec.yaml
│   ├── pubspec.lock
│   ├── android/
│   ├── ios/
│   └── test/
│       ├── unit/
│       ├── widget/
│       └── integration/
│
├── backend/
│   ├── main.py                      # Entry point
│   ├── requirements.txt             # Dependencies
│   ├── .env.example                 # Template
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app init
│   │   ├── config.py                # Settings from .env
│   │   ├── database.py              # Supabase connection
│   │   ├── dependencies.py          # Shared dependencies
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # POST /auth/signup, /auth/login, etc.
│   │   │   ├── products.py          # POST /products/upload, GET /products, etc.
│   │   │   ├── chat.py              # POST /chat/message, GET /chat/history
│   │   │   ├── orders.py            # GET /orders/search, GET /orders/{id}
│   │   │   ├── store.py             # GET /store/settings, PUT /store/settings
│   │   │   └── analytics.py         # GET /analytics/*
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   ├── conversation.py
│   │   │   ├── order.py
│   │   │   └── analytics_event.py
│   │   ├── schemas/                 # Pydantic validation schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   └── chat.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py      # Password hashing, JWT, password reset
│   │   │   ├── csv_service.py       # CSV parsing and validation
│   │   │   ├── gemini_service.py    # Gemini API integration
│   │   │   ├── order_service.py     # Order lookup logic
│   │   │   └── analytics_service.py # Event aggregation
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py
│   │       ├── error_handler.py
│   │       └── validators.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_products.py
│   │   └── test_chat.py
│   └── migrations/                  # SQL files for schema creation
│       ├── 001_create_users.sql
│       ├── 002_create_products.sql
│       ├── 003_create_conversations.sql
│       ├── 004_create_analytics_events.sql
│       └── 005_create_orders.sql
│
├── docs/
│   ├── README.md
│   ├── SETUP.md                     # How to set up dev environment
│   ├── API.md                       # API endpoint documentation
│   ├── DEPLOYMENT.md                # Production deployment guide
│   └── architecture.md              # This file
│
├── .gitignore
├── README.md
└── docker-compose.yml               # Optional: containerize backend
```

---

## Epic to Architecture Mapping

| Epic                                    | Goal                                     | Key Components                                            | Files                                                                         |
| --------------------------------------- | ---------------------------------------- | --------------------------------------------------------- | ----------------------------------------------------------------------------- |
| **1. Foundation & Auth**                | Backend, database, user authentication   | API server setup, JWT tokens, Supabase schema             | `backend/routers/auth.py`, `flutter_app/controllers/auth_controller.dart`     |
| **2. Product Upload & Admin Dashboard** | CSV upload, product management, settings | FastAPI upload handler, Hive storage, GetX controller     | `backend/routers/products.py`, `flutter_app/pages/owner/products_page.dart`   |
| **3. Customer Chat Interface**          | Chat UI, message display, history        | Chat controller, bubbles, typing indicator, optimistic UI | `flutter_app/pages/customer/chat_page.dart`, `chat_controller.dart`           |
| **4. Order Lookup & Status**            | Order search, status cards, timeline     | FastAPI search endpoint, order model, status widget       | `backend/routers/orders.py`, `flutter_app/widgets/order_status_card.dart`     |
| **5. Admin Analytics Dashboard**        | Event collection, charts, metrics        | Analytics service, fl_chart integration, aggregation      | `backend/routers/analytics.py`, `flutter_app/pages/owner/analytics_page.dart` |
| **6. Design System & Animations**       | Emerald theme, responsive UI, animations | Theme config, widgets, Lottie integration                 | `flutter_app/config/theme.dart`, `flutter_app/widgets/*`                      |
| **7. Performance & Infrastructure**     | Error handling, offline support, logging | ApiService, StorageService, error dialogs                 | `flutter_app/services/api_service.dart`, `logger_service.dart`                |

---

## Technology Stack Details

### Core Technologies

**Frontend (Flutter):**

- **Flutter:** 3.13+ (latest stable)
- **State Management:** GetX 4.6+
- **HTTP:** http package + custom ApiService
- **Local Storage:** Hive (fast key-value) + flutter_secure_storage (encrypted)
- **UI Components:** Material Design 3 (Flutter built-in)
- **Animations:** Native Flutter (transitions) + Lottie (complex)
- **Charts:** fl_chart
- **Image Loading:** cached_network_image
- **Date/Time:** intl (internationalization)

**Backend (FastAPI):**

- **Framework:** FastAPI 0.104+
- **Python:** 3.10+
- **Database:** Supabase PostgreSQL
- **Authentication:** JWT (PyJWT)
- **Password Hashing:** bcrypt (10+ rounds)
- **CSV Parsing:** Python csv module or pandas
- **HTTP Requests:** httpx (for Gemini API calls)
- **Environment:** python-dotenv

**External Services:**

- **Database:** Supabase (PostgreSQL + Auth)
- **AI:** Google Gemini 1.5 Flash API
- **Email (Optional):** SendGrid or Mailgun (for password resets in Pro tier)

### Verified Versions

| Package               | Current Stable | Verified Date |
| --------------------- | -------------- | ------------- |
| Flutter               | 3.16+          | Nov 2025      |
| GetX                  | 4.6+           | Nov 2025      |
| FastAPI               | 0.104+         | Nov 2025      |
| PostgreSQL (Supabase) | 15             | Nov 2025      |
| Python                | 3.10+          | Nov 2025      |
| Dart                  | 3.2+           | Nov 2025      |

---

## Data Architecture

### Database Schema (Supabase PostgreSQL)

**users table** (Store owners)

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  store_name VARCHAR(255),
  store_colors JSONB DEFAULT '{"primary":"#00a86b","accent":"#f97316"}',
  ai_tone VARCHAR(50) DEFAULT 'friendly',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_users_email ON users(email);
```

**products table** (Inventory)

```sql
CREATE TABLE products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  price DECIMAL(10,2) NOT NULL,
  category VARCHAR(100),
  sku VARCHAR(100),
  image_url VARCHAR(500),
  created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_products_user_id ON products(user_id);
CREATE INDEX idx_products_category ON products(category);
```

**conversations table** (Chat history)

```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  customer_message TEXT NOT NULL,
  ai_response TEXT NOT NULL,
  message_count INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
```

**analytics_events table** (Event tracking)

```sql
CREATE TABLE analytics_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  event_type VARCHAR(50),
  event_data JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_analytics_user_id ON analytics_events(user_id);
CREATE INDEX idx_analytics_created_at ON analytics_events(created_at);
```

**orders table** (Mock data for MVP)

```sql
CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  order_id VARCHAR(50) NOT NULL,
  customer_email VARCHAR(255),
  customer_name VARCHAR(255),
  items JSONB,
  total DECIMAL(10,2),
  status VARCHAR(50),
  estimated_delivery TIMESTAMP,
  tracking_number VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_order_id ON orders(order_id);
CREATE INDEX idx_orders_customer_email ON orders(customer_email);
```

**Row-Level Security (RLS):** Enabled on all tables so users see only their own data

---

## API Contracts

### Response Format (All Endpoints)

**Success Response:**

```json
{
  "success": true,
  "data": {
    /* actual content */
  },
  "message": "Optional human-readable message",
  "timestamp": "2025-11-15T10:30:00Z"
}
```

**Error Response:**

```json
{
  "success": false,
  "error": "Human-friendly error message",
  "code": "ERROR_CODE",
  "details": {
    /* debugging info */
  },
  "timestamp": "2025-11-15T10:30:00Z"
}
```

### Standard Error Codes

```
AUTH_INVALID_CREDENTIALS = "Invalid email or password"
AUTH_TOKEN_EXPIRED = "Your session expired, please log in again"
AUTH_UNAUTHORIZED = "You don't have permission for this"
VALIDATION_ERROR = "Invalid data submitted"
NETWORK_ERROR = "Network error, please check connection"
SERVER_ERROR = "Something went wrong, try again"
NOT_FOUND = "Resource not found"
```

### Key Endpoints

**Authentication:**

- `POST /auth/signup` - Create account
- `POST /auth/login` - Login
- `POST /auth/logout` - Logout
- `POST /auth/reset-password` - Request reset
- `POST /auth/reset-password-confirm` - Confirm reset

**Products:**

- `POST /products/upload` - Upload CSV
- `GET /products` - List products
- `GET /products/{id}` - Get product
- `DELETE /products/{id}` - Delete product
- `DELETE /products` - Delete all

**Chat:**

- `POST /chat/message` - Send message
- `GET /chat/history?limit=20&offset=0` - Get history

**Orders:**

- `GET /orders/search?query=ORD-123` - Search by order ID
- `GET /orders/search?query=email@example.com` - Search by email
- `GET /orders/{id}` - Get order details

**Store:**

- `GET /store/settings` - Get settings
- `PUT /store/settings` - Update settings

**Analytics:**

- `GET /analytics/events?days=7` - Get events
- `GET /analytics/questions-volume` - Volume chart data
- `GET /analytics/top-products` - Top products chart

---

## Implementation Patterns (Consistency Rules)

### Pattern 1: API Client Usage

**RULE: All HTTP requests must go through `api_service.dart`**

```dart
final response = await apiService.get('/products');
final response = await apiService.post('/chat/message', data: {...});
```

**Benefits:** Centralized error handling, auth headers, logging, easy URL switching

---

### Pattern 2: GetX Controllers

**RULE: All state changes must happen in GetX controllers**

```dart
class ChatController extends GetxController {
  final messages = <Conversation>[].obs;
  Future<void> sendMessage(String text) async { }
}
```

**Benefits:** Reactive UI updates, separation of concerns, testable

---

### Pattern 3: Error Handling

**RULE: All errors must show user-friendly dialog**

```dart
Get.snackbar('Error', 'Could not send message. Try again.');
```

**Benefits:** Better UX, consistent error display

---

### Pattern 4: Model Serialization

**RULE: All models must have `toJson()` and `fromJson()`**

```dart
class Conversation {
  factory Conversation.fromJson(Map<String, dynamic> json) { }
  Map<String, dynamic> toJson() { }
}
```

**Benefits:** Consistent data handling, easy API integration

---

### Pattern 5: Local Storage

**RULE: All storage goes through `StorageService`**

```dart
await storageService.saveConversations(messages);
final cached = await storageService.getConversations();
```

**Benefits:** Centralized access, easy to change implementation

---

### Pattern 6: Widget Organization

**RULE: Custom widgets go in `/widgets` with clear naming**

```
chat_bubble.dart       - Shows one message
product_card.dart      - Shows one product
order_status_card.dart - Shows one order status
```

**Benefits:** Reusable, discoverable, organized

---

### Pattern 7: Navigation

**RULE: Use GetX named routes**

```dart
Get.toNamed('/chat');
Get.toNamed('/order-details', arguments: {'orderId': '123'});
```

**Benefits:** Centralized routing, easy to track, no context needed

---

### Pattern 8: Code Style

**RULE: Follow Dart style guide + run `dart format`**

```bash
flutter analyze    # Check style
dart format lib/   # Auto-format
```

**Benefits:** Consistent, professional, easy to read

---

## Consistency Rules

### Naming Conventions

**Classes:** PascalCase

```dart
class ChatController { }
class ProductCard { }
class UserModel { }
```

**Functions/Methods:** camelCase

```dart
void sendMessage() { }
Future<List<Product>> fetchProducts() { }
```

**Variables:** camelCase

```dart
final userEmail = '';
final isLoading = false;
```

**Constants:** UPPER_SNAKE_CASE (or camelCase for const)

```dart
const String apiBaseUrl = 'https://api.example.com';
const String keyApiToken = 'api_token';
```

**Files:** snake_case

```
chat_controller.dart
product_card.dart
api_service.dart
```

### Code Organization

**File layout:**

```dart
// 1. Imports
import 'package:flutter/material.dart';
import 'package:get/get.dart';

// 2. Constants
const int maxRetries = 3;

// 3. Class definition
class ChatController extends GetxController {
  // 3a. Variables
  final isLoading = false.obs;

  // 3b. Lifecycle
  @override
  void onInit() { }

  // 3c. Getters
  bool get isChatEmpty => messages.isEmpty;

  // 3d. Methods
  Future<void> sendMessage() { }
}
```

### Error Handling Approach

**Always provide recovery:**

- Network error → "Retry" button
- Validation error → "Fix and try again"
- API error → "Retry" or "Contact support"

**Error messages format:** "What happened. Why. What to do."

- Bad: "Connection refused"
- Good: "No internet connection. Please check WiFi and try again."

### Logging Strategy

**Log these:**

- User actions (login, message send, CSV upload)
- API requests/responses (success + failures)
- Errors (with stack trace)

**Never log:**

- Passwords, tokens, sensitive data
- Full PII (use IDs instead)
- Massive datasets

---

## Security Architecture

### Authentication

- **Password Hashing:** bcrypt (10+ rounds, not reversible)
- **Session Token:** JWT with 7-day expiration
- **Token Storage:** flutter_secure_storage (encrypted on device)
- **HTTPS Only:** All API calls use HTTPS
- **Password Reset:** 15-minute expiry tokens

### Authorization

- **Row-Level Security (RLS):** Supabase RLS policies
- **Each user only sees their own data**
- **Backend validates user_id on every request**

### Data Protection

- **No sensitive data in logs**
- **Passwords never in transit** (JWT tokens used instead)
- **Database backups:** Supabase handles automatically
- **Secure storage:** Tokens in encrypted storage, passwords never stored locally

---

## Performance Considerations

### Targets

- **App startup:** < 3 seconds
- **Chat response latency:** < 2 seconds
- **CSV upload:** < 5 seconds (1000 products)
- **Frame rate:** 60 FPS (no jank)
- **Memory:** < 150MB
- **Local cache:** < 50MB

### Strategies

**Startup:**

- Lazy load controllers (use GetX's .get() on-demand)
- Cache Hive boxes at app startup
- Async initialization for heavy work

**Chat Response:**

- Show typing indicator immediately (optimistic UI)
- Cache product context locally
- Use HTTP/2 for API calls

**CSV Upload:**

- Show progress bar with visual feedback
- Validate in batches, not one-by-one
- Display success/error count clearly

**Memory:**

- Pagination for lists (load 20 at a time)
- Image caching (cached_network_image)
- Release resources in controller onClose()

**Frame Rate:**

- Use simple animations (avoid complex shapes)
- Profile with DevTools
- Test on low-end devices (minimum target device)

---

## Deployment Architecture

### Development Environment

```bash
flutter run              # Run on emulator/device
flutter pub get         # Get dependencies
dart format lib/        # Format code
flutter analyze         # Check for issues
flutter test            # Run tests
```

### Backend Development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload  # Auto-restart on changes
```

### Production Deployment (Future)

**Flutter App:**

- Build: `flutter build apk` (Android) or `flutter build ios` (iOS)
- Deploy to: Google Play Store + Apple App Store

**Backend:**

- Deploy to: Vercel, Railway, or DigitalOcean
- Database: Supabase (managed)
- Monitoring: Sentry (error tracking)

---

## Development Environment Setup

### Prerequisites

- **Flutter:** 3.13+
- **Dart:** 3.2+
- **Python:** 3.10+
- **Git:** 2.0+
- **Android Studio** (for Android) or **Xcode** (for iOS)
- **Supabase account** (free tier suitable for MVP)
- **Google Cloud account** (for Gemini API key)

### Setup Commands

```bash
# Clone repository
git clone <repo-url>
cd shopify_mind_ai

# Flutter setup
flutter pub get
flutter create --platforms=android,ios .  # If needed

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Create .env file (copy from .env.example)
cp .env.example .env
# Edit .env with your Supabase URL, Gemini API key, etc.

# Run backend
uvicorn app.main:app --reload

# In new terminal, run Flutter
cd ../flutter_app
flutter run -d <device-id>  # or just 'flutter run' to pick device
```

---

## Architecture Decision Records (ADRs)

### ADR-001: FastAPI Backend

**Decision:** Use FastAPI (Python) for backend, not Express (Node.js)

**Rationale:**

- Fast development (auto-validation, auto-docs)
- Faster time-to-market for 4-day MVP
- Clear error messages help debugging
- Excellent for first-time backend builders

**Trade-offs:**

- Slightly slower than Node.js
- Smaller ecosystem for some packages
- Not an issue for this project scale

---

### ADR-002: GetX State Management

**Decision:** Use GetX for state management, not Provider or BLoC

**Rationale:**

- Minimal boilerplate (fast to code)
- Reactive (automatic UI updates)
- Built-in routing and dependency injection
- Perfect for 4-day MVP timeline

**Trade-offs:**

- Learning curve for reactive concepts
- Less popular than Provider (but growing)
- Not an issue for feature-focused development

---

### ADR-003: JWT Authentication

**Decision:** Use JWT tokens, not session-based auth

**Rationale:**

- Stateless (backend doesn't remember sessions)
- Mobile-friendly (no cookies needed)
- Scales easily to multiple backend instances
- Industry standard for mobile apps

**Trade-offs:**

- Token revocation requires blacklist (we skip for MVP)
- Slightly more complex than session cookies
- Not an issue for startup project

---

### ADR-004: Hive Local Storage

**Decision:** Use Hive for local caching, not SQLite

**Rationale:**

- Super fast (key-value, no SQL queries)
- Works perfectly with GetX (reactive)
- Minimal setup (no migrations)
- Lightweight

**Trade-offs:**

- Less flexible than SQLite
- Query limitations
- Not an issue - we don't need complex queries for MVP

---

### ADR-005: Supabase Database

**Decision:** Use Supabase (PostgreSQL), not Firebase

**Rationale:**

- Row-level security (perfect for multi-tenant)
- Built-in auth (JWT support)
- Real-time updates (future-proof)
- Free tier sufficient for MVP

**Trade-offs:**

- Requires more setup than Firebase
- PostgreSQL knowledge helpful
- Perfect match for our needs

---

## Next Steps

1. **Epic 1 (Foundation):** Set up backend, database schema, auth endpoints
2. **Epic 2 (Products):** CSV upload endpoint + Flutter upload UI
3. **Epic 3 (Chat):** Chat interface + Gemini integration
4. **Epic 4 (Orders):** Order lookup + status cards
5. **Epic 5 (Analytics):** Event collection + dashboard
6. **Epic 6 (Design):** Polish animations, theme consistency
7. **Epic 7 (Performance):** Testing, optimization, error handling

---

## Related Documents

- **[API.md](API.md)** - Detailed API endpoint documentation
- **[SETUP.md](SETUP.md)** - Developer environment setup guide
- **[PRD.md](../PRD.md)** - Product requirements
- **[epics.md](../epics.md)** - Epic & story breakdown
- **[ux-design-specification.md](../ux-design-specification.md)** - UX specifications

---

**Architecture complete and ready for implementation.**

_Generated by Winston (Architect Agent) on November 15, 2025_
_Based on collaborative discovery with BMad_
