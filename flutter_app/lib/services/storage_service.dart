import 'package:hive_flutter/hive_flutter.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/constants.dart';
import '../models/conversation.dart';
import 'logger_service.dart';

/// Centralized storage service for local data persistence
/// Uses Hive for general storage, FlutterSecureStorage for sensitive data
class StorageService {
  final LoggerService _logger;
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();
  SharedPreferences? _prefs;

  StorageService(this._logger);

  /// Initialize storage
  Future<void> init() async {
    try {
      // Initialize Hive
      await Hive.initFlutter();

      // Register adapters
      // Hive.registerAdapter(ConversationAdapter());

      // Open boxes
      await Hive.openBox<Conversation>(AppConstants.hiveBoxConversations);
      await Hive.openBox(AppConstants.hiveBoxProducts);
      await Hive.openBox(AppConstants.hiveBoxSettings);

      // Initialize SharedPreferences
      _prefs = await SharedPreferences.getInstance();

      _logger.logInfo('Storage service initialized');
    } catch (e) {
      _logger.logError('Failed to initialize storage: $e');
      rethrow;
    }
  }

  // ==========================================
  // Secure Storage (for sensitive data)
  // ==========================================

  /// Save to secure storage
  Future<void> saveSecure(String key, String value) async {
    try {
      await _secureStorage.write(key: key, value: value);
      _logger.logDebug('Saved to secure storage: $key');
    } catch (e) {
      _logger.logError('Failed to save to secure storage: $e');
      rethrow;
    }
  }

  /// Read from secure storage
  Future<String?> readSecure(String key) async {
    try {
      return await _secureStorage.read(key: key);
    } catch (e) {
      _logger.logError('Failed to read from secure storage: $e');
      return null;
    }
  }

  /// Delete from secure storage
  Future<void> deleteSecure(String key) async {
    try {
      await _secureStorage.delete(key: key);
      _logger.logDebug('Deleted from secure storage: $key');
    } catch (e) {
      _logger.logError('Failed to delete from secure storage: $e');
    }
  }

  /// Clear all secure storage
  Future<void> clearSecure() async {
    try {
      await _secureStorage.deleteAll();
      _logger.logInfo('Cleared all secure storage');
    } catch (e) {
      _logger.logError('Failed to clear secure storage: $e');
    }
  }

  // ==========================================
  // Shared Preferences (for simple key-value pairs)
  // ==========================================

  /// Save string to preferences
  Future<void> saveString(String key, String value) async {
    await _prefs?.setString(key, value);
  }

  /// Read string from preferences
  String? readString(String key) {
    return _prefs?.getString(key);
  }

  /// Save bool to preferences
  Future<void> saveBool(String key, bool value) async {
    await _prefs?.setBool(key, value);
  }

  /// Read bool from preferences
  bool? readBool(String key) {
    return _prefs?.getBool(key);
  }

  /// Save int to preferences
  Future<void> saveInt(String key, int value) async {
    await _prefs?.setInt(key, value);
  }

  /// Read int from preferences
  int? readInt(String key) {
    return _prefs?.getInt(key);
  }

  /// Remove from preferences
  Future<void> remove(String key) async {
    await _prefs?.remove(key);
  }

  /// Clear all preferences
  Future<void> clearPreferences() async {
    await _prefs?.clear();
  }

  // ==========================================
  // Hive Storage (for structured data)
  // ==========================================

  /// Get Hive box
  Box<T> getBox<T>(String boxName) {
    return Hive.box<T>(boxName);
  }

  /// Save conversation
  Future<void> saveConversation(Conversation conversation) async {
    try {
      final box = getBox<Conversation>(AppConstants.hiveBoxConversations);
      await box.put(conversation.id, conversation);
      _logger.logDebug('Saved conversation: ${conversation.id}');
    } catch (e) {
      _logger.logError('Failed to save conversation: $e');
    }
  }

  /// Get all conversations
  List<Conversation> getConversations() {
    try {
      final box = getBox<Conversation>(AppConstants.hiveBoxConversations);
      return box.values.toList();
    } catch (e) {
      _logger.logError('Failed to get conversations: $e');
      return [];
    }
  }

  /// Get conversation by ID
  Conversation? getConversation(String id) {
    try {
      final box = getBox<Conversation>(AppConstants.hiveBoxConversations);
      return box.get(id);
    } catch (e) {
      _logger.logError('Failed to get conversation: $e');
      return null;
    }
  }

  /// Delete conversation
  Future<void> deleteConversation(String id) async {
    try {
      final box = getBox<Conversation>(AppConstants.hiveBoxConversations);
      await box.delete(id);
      _logger.logDebug('Deleted conversation: $id');
    } catch (e) {
      _logger.logError('Failed to delete conversation: $e');
    }
  }

  /// Clear all conversations
  Future<void> clearConversations() async {
    try {
      final box = getBox<Conversation>(AppConstants.hiveBoxConversations);
      await box.clear();
      _logger.logInfo('Cleared all conversations');
    } catch (e) {
      _logger.logError('Failed to clear conversations: $e');
    }
  }

  /// Save generic data to box
  Future<void> saveToBox(String boxName, String key, dynamic value) async {
    try {
      final box = getBox(boxName);
      await box.put(key, value);
      _logger.logDebug('Saved to box $boxName: $key');
    } catch (e) {
      _logger.logError('Failed to save to box: $e');
    }
  }

  /// Get generic data from box
  dynamic getFromBox(String boxName, String key) {
    try {
      final box = getBox(boxName);
      return box.get(key);
    } catch (e) {
      _logger.logError('Failed to get from box: $e');
      return null;
    }
  }

  /// Clear specific box
  Future<void> clearBox(String boxName) async {
    try {
      final box = getBox(boxName);
      await box.clear();
      _logger.logInfo('Cleared box: $boxName');
    } catch (e) {
      _logger.logError('Failed to clear box: $e');
    }
  }

  /// Close all boxes (call on app termination)
  Future<void> closeAll() async {
    await Hive.close();
    _logger.logInfo('Closed all storage boxes');
  }
}
