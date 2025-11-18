import 'package:logger/logger.dart';
import '../config/constants.dart';

/// Centralized logging service
/// Handles all app logging with different severity levels
class LoggerService {
  late final Logger _logger;

  LoggerService() {
    _logger = Logger(
      printer: PrettyPrinter(
        methodCount: 0,
        errorMethodCount: 5,
        lineLength: 80,
        colors: true,
        printEmojis: true,
        dateTimeFormat: DateTimeFormat.onlyTimeAndSinceStart,
      ),
      level: AppConstants.enableDebugLogging ? Level.debug : Level.info,
    );
  }

  /// Log debug message
  void logDebug(String message, [dynamic error, StackTrace? stackTrace]) {
    if (AppConstants.enableDebugLogging) {
      _logger.d(message, error: error, stackTrace: stackTrace);
    }
  }

  /// Log info message
  void logInfo(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.i(message, error: error, stackTrace: stackTrace);
  }

  /// Log warning message
  void logWarning(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.w(message, error: error, stackTrace: stackTrace);
  }

  /// Log error message
  void logError(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.e(message, error: error, stackTrace: stackTrace);
  }

  /// Log fatal/critical error
  void logFatal(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.f(message, error: error, stackTrace: stackTrace);
  }

  /// Log API request
  void logApiRequest(String method, String endpoint) {
    logDebug('API Request: $method $endpoint');
  }

  /// Log API response
  void logApiResponse(int statusCode, String endpoint) {
    logDebug('API Response: $statusCode from $endpoint');
  }

  /// Log user action
  void logUserAction(String action, [Map<String, dynamic>? data]) {
    logInfo('User Action: $action${data != null ? ' - $data' : ''}');
  }

  /// Log navigation
  void logNavigation(String from, String to) {
    logDebug('Navigation: $from -> $to');
  }

  /// Log performance metric
  void logPerformance(String operation, Duration duration) {
    logInfo('Performance: $operation took ${duration.inMilliseconds}ms');
  }

  /// Close logger (if needed)
  void close() {
    _logger.close();
  }
}
