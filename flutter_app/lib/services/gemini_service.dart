import 'api_service.dart';
import 'logger_service.dart';
import '../config/constants.dart';

/// Service for handling Gemini AI interactions through backend
/// Note: Gemini API calls are handled by the backend, not directly from app
class GeminiService {
  final ApiService _apiService;
  final LoggerService _logger;

  GeminiService(this._apiService, this._logger);

  /// Send message to AI and get response
  Future<ChatResponse?> sendMessage(
    String message, {
    String? customerIdentifier,
    String? sessionId,
  }) async {
    try {
      _logger.logInfo('Sending message to AI: ${message.substring(0, 50)}...');

      final response = await _apiService.post(
        AppConstants.chatMessage,
        data: {
          'message': message,
          'customer_identifier': customerIdentifier,
          'session_id': sessionId,
        },
        timeout: AppConstants.chatTimeout,
      );

      if (response.isSuccess) {
        final chatResponse = ChatResponse.fromJson(response.data);
        _logger.logInfo(
            'AI response received: ${chatResponse.aiResponse.substring(0, 50)}...');
        return chatResponse;
      } else {
        _logger.logError('AI response failed: ${response.message}');
        return null;
      }
    } catch (e) {
      _logger.logError('Failed to send message: $e');
      return null;
    }
  }

  /// Get chat history
  Future<List<ChatHistoryItem>> getChatHistory({
    int limit = 20,
    int offset = 0,
    String? customerIdentifier,
  }) async {
    try {
      final queryParams = {
        'limit': limit.toString(),
        'offset': offset.toString(),
      };

      if (customerIdentifier != null) {
        queryParams['customer_identifier'] = customerIdentifier;
      }

      final response = await _apiService.get(
        AppConstants.chatHistory,
        queryParams: queryParams,
      );

      if (response.isSuccess) {
        final conversations = (response.data['conversations'] as List<dynamic>)
            .map((e) => ChatHistoryItem.fromJson(e as Map<String, dynamic>))
            .toList();

        _logger.logInfo('Retrieved ${conversations.length} chat messages');
        return conversations;
      } else {
        _logger.logError('Failed to get chat history: ${response.message}');
        return [];
      }
    } catch (e) {
      _logger.logError('Failed to get chat history: $e');
      return [];
    }
  }

  /// Clear chat history
  Future<bool> clearChatHistory() async {
    try {
      final response = await _apiService.delete(AppConstants.chatHistory);

      if (response.isSuccess) {
        _logger.logInfo('Chat history cleared');
        return true;
      } else {
        _logger.logError('Failed to clear chat history: ${response.message}');
        return false;
      }
    } catch (e) {
      _logger.logError('Failed to clear chat history: $e');
      return false;
    }
  }
}

/// Chat response from AI
class ChatResponse {
  final String id;
  final String customerMessage;
  final String aiResponse;
  final List<ProductCard> products;
  final String? intentDetected;
  final int responseTimeMs;

  ChatResponse({
    required this.id,
    required this.customerMessage,
    required this.aiResponse,
    this.products = const [],
    this.intentDetected,
    required this.responseTimeMs,
  });

  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    return ChatResponse(
      id: json['id'] as String,
      customerMessage: json['customer_message'] as String,
      aiResponse: json['ai_response'] as String,
      products: (json['products'] as List<dynamic>?)
              ?.map((e) => ProductCard.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      intentDetected: json['intent_detected'] as String?,
      responseTimeMs: json['response_time_ms'] as int,
    );
  }
}

/// Product card in chat response
class ProductCard {
  final String id;
  final String name;
  final String? description;
  final double price;
  final String? category;
  final String? imageUrl;

  ProductCard({
    required this.id,
    required this.name,
    this.description,
    required this.price,
    this.category,
    this.imageUrl,
  });

  factory ProductCard.fromJson(Map<String, dynamic> json) {
    return ProductCard(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      price: (json['price'] as num).toDouble(),
      category: json['category'] as String?,
      imageUrl: json['image_url'] as String?,
    );
  }
}

/// Chat history item
class ChatHistoryItem {
  final String id;
  final String message;
  final String response;
  final DateTime timestamp;
  final String? customerIdentifier;
  final String? intentDetected;

  ChatHistoryItem({
    required this.id,
    required this.message,
    required this.response,
    required this.timestamp,
    this.customerIdentifier,
    this.intentDetected,
  });

  factory ChatHistoryItem.fromJson(Map<String, dynamic> json) {
    return ChatHistoryItem(
      id: json['id'] as String,
      message: json['message'] as String,
      response: json['response'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      customerIdentifier: json['customer_identifier'] as String?,
      intentDetected: json['intent_detected'] as String?,
    );
  }
}
