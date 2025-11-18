import '../config/constants.dart';
import '../models/user.dart';
import 'storage_service.dart';
import 'logger_service.dart';

/// Authentication service handling user authentication and token management
class AuthService {
  final StorageService _storage;
  final LoggerService _logger;

  User? _currentUser;
  String? _authToken;

  AuthService(this._storage, this._logger);

  /// Check if user is authenticated
  bool get isAuthenticated => _authToken != null;

  /// Get current user
  User? get currentUser => _currentUser;

  /// Get auth token
  Future<String?> getToken() async {
    if (_authToken != null) return _authToken;

    // Try to load from secure storage
    _authToken = await _storage.readSecure(AppConstants.keyAuthToken);
    return _authToken;
  }

  /// Initialize auth (check for saved session)
  Future<bool> init() async {
    try {
      _authToken = await _storage.readSecure(AppConstants.keyAuthToken);

      if (_authToken != null) {
        // Token exists, try to get user info
        final userId = await _storage.readSecure(AppConstants.keyUserId);
        final userEmail = await _storage.readSecure(AppConstants.keyUserEmail);

        if (userId != null && userEmail != null) {
          // Create user object from stored data
          // In a real app, you might want to fetch fresh user data from API
          _currentUser = User(
            id: userId,
            email: userEmail,
            storeColors: StoreColors(
              primary: '#00a86b',
              accent: '#f97316',
              supporting: '#a78bfa',
            ),
            aiTone: 'friendly',
          );

          _logger.logInfo('User session restored: ${_currentUser!.email}');
          return true;
        }
      }

      return false;
    } catch (e) {
      _logger.logError('Failed to initialize auth: $e');
      return false;
    }
  }

  /// Save authentication data
  Future<void> saveAuth(AuthResponse authResponse, User user) async {
    try {
      _authToken = authResponse.token;
      _currentUser = user;

      // Save to secure storage
      await _storage.saveSecure(AppConstants.keyAuthToken, authResponse.token);
      await _storage.saveSecure(AppConstants.keyUserId, authResponse.userId);
      await _storage.saveSecure(AppConstants.keyUserEmail, authResponse.email);

      // Save store settings to preferences
      if (user.storeName != null) {
        await _storage.saveString(AppConstants.keyStoreName, user.storeName!);
      }
      await _storage.saveString(AppConstants.keyAiTone, user.aiTone);

      _logger.logInfo('Auth saved for user: ${authResponse.email}');
    } catch (e) {
      _logger.logError('Failed to save auth: $e');
      rethrow;
    }
  }

  /// Update current user
  void updateUser(User user) {
    _currentUser = user;
    _logger.logDebug('User updated: ${user.email}');
  }

  /// Clear authentication data
  Future<void> clearAuth() async {
    try {
      _authToken = null;
      _currentUser = null;

      // Clear secure storage
      await _storage.deleteSecure(AppConstants.keyAuthToken);
      await _storage.deleteSecure(AppConstants.keyUserId);
      await _storage.deleteSecure(AppConstants.keyUserEmail);

      // Clear preferences
      await _storage.remove(AppConstants.keyStoreName);
      await _storage.remove(AppConstants.keyAiTone);

      // Clear cached conversations
      await _storage.clearConversations();

      _logger.logInfo('Auth cleared');
    } catch (e) {
      _logger.logError('Failed to clear auth: $e');
    }
  }

  /// Validate email format
  bool validateEmail(String email) {
    return AppConstants.isValidEmail(email);
  }

  /// Validate password format
  bool validatePassword(String password) {
    return AppConstants.isValidPassword(password);
  }

  /// Get stored store name
  String? getStoreName() {
    return _storage.readString(AppConstants.keyStoreName);
  }

  /// Get stored AI tone
  String? getAiTone() {
    return _storage.readString(AppConstants.keyAiTone);
  }
}
