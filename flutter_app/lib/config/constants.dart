/// Application constants and configuration values
class AppConstants {
  // ==========================================
  // App Information
  // ==========================================

  static const String appName = 'ShopifyMind AI';
  static const String appVersion = '1.0.0';

  // ==========================================
  // API Configuration
  // ==========================================

  /// Base URL for backend API
  /// Change this to your production URL when deploying
  static const String apiBaseUrl = 'http://localhost:8000';

  /// Supabase configuration
  static const String supabaseUrl = 'YOUR_SUPABASE_URL';
  static const String supabaseAnonKey = 'YOUR_SUPABASE_ANON_KEY';

  // ==========================================
  // API Endpoints
  // ==========================================

  /// Authentication endpoints
  static const String authSignup = '/auth/signup';
  static const String authLogin = '/auth/login';
  static const String authLogout = '/auth/logout';
  static const String authMe = '/auth/me';
  static const String authResetPassword = '/auth/reset-password';

  /// Product endpoints
  static const String productsUpload = '/products/upload';
  static const String products = '/products';

  /// Chat endpoints
  static const String chatMessage = '/chat/message';
  static const String chatHistory = '/chat/history';

  /// Order endpoints
  static const String ordersSearch = '/orders/search';
  static const String orders = '/orders';

  /// Store endpoints
  static const String storeSettings = '/store/settings';
  static const String storeStats = '/store/stats';

  /// Analytics endpoints
  static const String analyticsSummary = '/analytics/summary';
  static const String analyticsQuestionsVolume = '/analytics/questions-volume';
  static const String analyticsTopProducts = '/analytics/top-products';
  static const String analyticsEngagement = '/analytics/engagement';

  // ==========================================
  // Timeouts
  // ==========================================

  /// API request timeout duration
  static const Duration apiTimeout = Duration(seconds: 15);

  /// Chat response timeout duration
  static const Duration chatTimeout = Duration(seconds: 10);

  /// Connection timeout duration
  static const Duration connectionTimeout = Duration(seconds: 30);

  // ==========================================
  // Storage Keys
  // ==========================================

  /// Secure storage keys (flutter_secure_storage)
  static const String keyAuthToken = 'auth_token';
  static const String keyUserId = 'user_id';
  static const String keyUserEmail = 'user_email';

  /// Hive box names
  static const String hiveBoxConversations = 'conversations';
  static const String hiveBoxProducts = 'products';
  static const String hiveBoxSettings = 'settings';

  /// Shared preferences keys
  static const String keyStoreColors = 'store_colors';
  static const String keyStoreName = 'store_name';
  static const String keyAiTone = 'ai_tone';
  static const String keyIsFirstLaunch = 'is_first_launch';

  // ==========================================
  // Error Messages
  // ==========================================

  /// Network error message
  static const String networkError =
      'No internet connection. Please check your network and try again.';

  /// Server error message
  static const String serverError =
      'Something went wrong on our end. Please try again later.';

  /// Authentication error message
  static const String authError = 'Authentication failed. Please log in again.';

  /// Validation error message
  static const String validationError =
      'Please check your input and try again.';

  /// Timeout error message
  static const String timeoutError =
      'Request timed out. Please check your connection and try again.';

  /// Unknown error message
  static const String unknownError =
      'An unexpected error occurred. Please try again.';

  /// File upload error message
  static const String fileUploadError =
      'Failed to upload file. Please try again.';

  // ==========================================
  // Error Codes (from backend)
  // ==========================================

  static const String errorCodeAuthInvalidCredentials =
      'AUTH_INVALID_CREDENTIALS';
  static const String errorCodeAuthTokenExpired = 'AUTH_TOKEN_EXPIRED';
  static const String errorCodeAuthUnauthorized = 'AUTH_UNAUTHORIZED';
  static const String errorCodeValidationError = 'VALIDATION_ERROR';
  static const String errorCodeNetworkError = 'NETWORK_ERROR';
  static const String errorCodeServerError = 'SERVER_ERROR';
  static const String errorCodeNotFound = 'NOT_FOUND';

  // ==========================================
  // Pagination
  // ==========================================

  /// Default page size for lists
  static const int defaultPageSize = 20;

  /// Maximum page size
  static const int maxPageSize = 100;

  // ==========================================
  // File Upload
  // ==========================================

  /// Maximum CSV file size (10MB)
  static const int maxCsvFileSize = 10 * 1024 * 1024;

  /// Maximum products per upload
  static const int maxProductsPerUpload = 1000;

  /// Allowed file extensions
  static const List<String> allowedCsvExtensions = ['.csv'];

  // ==========================================
  // Chat Configuration
  // ==========================================

  /// Maximum message length
  static const int maxMessageLength = 2000;

  /// Minimum message length
  static const int minMessageLength = 1;

  /// Number of messages to load per page
  static const int messagesPerPage = 20;

  /// Typing indicator delay (milliseconds)
  static const int typingIndicatorDelay = 500;

  // ==========================================
  // Animation Durations
  // ==========================================

  /// Short animation duration
  static const Duration animationShort = Duration(milliseconds: 150);

  /// Medium animation duration
  static const Duration animationMedium = Duration(milliseconds: 250);

  /// Long animation duration
  static const Duration animationLong = Duration(milliseconds: 400);

  // ==========================================
  // Analytics
  // ==========================================

  /// Default analytics time range (days)
  static const int defaultAnalyticsDays = 7;

  /// Maximum analytics time range (days)
  static const int maxAnalyticsDays = 90;

  // ==========================================
  // Regular Expressions
  // ==========================================

  /// Email validation regex
  static final RegExp emailRegex = RegExp(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
  );

  /// Password validation regex (minimum 8 characters)
  static final RegExp passwordRegex = RegExp(
    r'^.{8,}$',
  );

  /// URL validation regex
  static final RegExp urlRegex = RegExp(
    r'^https?:\/\/',
  );

  // ==========================================
  // Feature Flags
  // ==========================================

  /// Enable debug logging
  static const bool enableDebugLogging = true;

  /// Enable analytics
  static const bool enableAnalytics = true;

  /// Enable error reporting
  static const bool enableErrorReporting = true;

  /// Enable offline mode
  static const bool enableOfflineMode = true;

  // ==========================================
  // UI Constants
  // ==========================================

  /// Minimum touch target size (accessibility)
  static const double minTouchTargetSize = 44.0;

  /// Maximum content width for tablets
  static const double maxContentWidth = 600.0;

  /// Default image placeholder
  static const String placeholderImage = 'assets/images/placeholder.png';

  /// Empty state animation
  static const String emptyStateAnimation =
      'assets/animations/empty_state.json';

  /// Loading animation
  static const String loadingAnimation = 'assets/animations/loading.json';

  /// Typing indicator animation
  static const String typingIndicatorAnimation =
      'assets/animations/typing_indicator.json';

  // ==========================================
  // Date/Time Formats
  // ==========================================

  /// Date format for display
  static const String displayDateFormat = 'MMM dd, yyyy';

  /// Time format for display
  static const String displayTimeFormat = 'hh:mm a';

  /// Full date-time format
  static const String fullDateTimeFormat = 'MMM dd, yyyy hh:mm a';

  /// ISO 8601 format (for API)
  static const String isoDateTimeFormat = "yyyy-MM-dd'T'HH:mm:ss'Z'";

  // ==========================================
  // Helper Methods
  // ==========================================

  /// Get full API URL
  static String getApiUrl(String endpoint) {
    return '$apiBaseUrl$endpoint';
  }

  /// Check if email is valid
  static bool isValidEmail(String email) {
    return emailRegex.hasMatch(email);
  }

  /// Check if password is valid
  static bool isValidPassword(String password) {
    return passwordRegex.hasMatch(password);
  }

  /// Check if URL is valid
  static bool isValidUrl(String url) {
    return urlRegex.hasMatch(url);
  }

  /// Get friendly error message from error code
  static String getErrorMessage(String? errorCode) {
    switch (errorCode) {
      case errorCodeAuthInvalidCredentials:
        return 'Invalid email or password. Please try again.';
      case errorCodeAuthTokenExpired:
        return 'Your session has expired. Please log in again.';
      case errorCodeAuthUnauthorized:
        return 'You do not have permission to perform this action.';
      case errorCodeValidationError:
        return validationError;
      case errorCodeNetworkError:
        return networkError;
      case errorCodeServerError:
        return serverError;
      case errorCodeNotFound:
        return 'The requested resource was not found.';
      default:
        return unknownError;
    }
  }
}
