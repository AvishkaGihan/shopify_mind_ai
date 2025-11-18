import 'package:hive/hive.dart';

part 'conversation.g.dart';

/// Conversation model representing chat messages
@HiveType(typeId: 0)
class Conversation {
  @HiveField(0)
  final String id;

  @HiveField(1)
  final String userId;

  @HiveField(2)
  final String? customerIdentifier;

  @HiveField(3)
  final String customerMessage;

  @HiveField(4)
  final String aiResponse;

  @HiveField(5)
  final int messageCount;

  @HiveField(6)
  final List<String> productsReferenced;

  @HiveField(7)
  final String? intentDetected;

  @HiveField(8)
  final double? sentimentScore;

  @HiveField(9)
  final int? responseTimeMs;

  @HiveField(10)
  final DateTime createdAt;

  Conversation({
    required this.id,
    required this.userId,
    this.customerIdentifier,
    required this.customerMessage,
    required this.aiResponse,
    this.messageCount = 1,
    this.productsReferenced = const [],
    this.intentDetected,
    this.sentimentScore,
    this.responseTimeMs,
    required this.createdAt,
  });

  factory Conversation.fromJson(Map<String, dynamic> json) {
    return Conversation(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      customerIdentifier: json['customer_identifier'] as String?,
      customerMessage: json['customer_message'] as String,
      aiResponse: json['ai_response'] as String,
      messageCount: json['message_count'] as int? ?? 1,
      productsReferenced: (json['products_referenced'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          [],
      intentDetected: json['intent_detected'] as String?,
      sentimentScore: json['sentiment_score'] as double?,
      responseTimeMs: json['response_time_ms'] as int?,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'customer_identifier': customerIdentifier,
      'customer_message': customerMessage,
      'ai_response': aiResponse,
      'message_count': messageCount,
      'products_referenced': productsReferenced,
      'intent_detected': intentDetected,
      'sentiment_score': sentimentScore,
      'response_time_ms': responseTimeMs,
      'created_at': createdAt.toIso8601String(),
    };
  }

  /// Convert to chat display format
  Map<String, dynamic> toChatJson() {
    return {
      'id': id,
      'message': customerMessage,
      'response': aiResponse,
      'timestamp': createdAt.toIso8601String(),
      'products': productsReferenced,
    };
  }

  Conversation copyWith({
    String? id,
    String? userId,
    String? customerIdentifier,
    String? customerMessage,
    String? aiResponse,
    int? messageCount,
    List<String>? productsReferenced,
    String? intentDetected,
    double? sentimentScore,
    int? responseTimeMs,
    DateTime? createdAt,
  }) {
    return Conversation(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      customerIdentifier: customerIdentifier ?? this.customerIdentifier,
      customerMessage: customerMessage ?? this.customerMessage,
      aiResponse: aiResponse ?? this.aiResponse,
      messageCount: messageCount ?? this.messageCount,
      productsReferenced: productsReferenced ?? this.productsReferenced,
      intentDetected: intentDetected ?? this.intentDetected,
      sentimentScore: sentimentScore ?? this.sentimentScore,
      responseTimeMs: responseTimeMs ?? this.responseTimeMs,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  String toString() {
    return 'Conversation(id: $id, message: ${customerMessage.substring(0, 20)}...)';
  }
}

/// Message intent types
class MessageIntent {
  static const String productInquiry = 'product_inquiry';
  static const String orderLookup = 'order_lookup';
  static const String generalQuestion = 'general_question';
  static const String complaint = 'complaint';
  static const String praise = 'praise';
  static const String shippingQuestion = 'shipping_question';
  static const String returnRequest = 'return_request';
  static const String unknown = 'unknown';

  static String getDisplayName(String intent) {
    switch (intent) {
      case productInquiry:
        return 'Product Question';
      case orderLookup:
        return 'Order Lookup';
      case generalQuestion:
        return 'General Question';
      case complaint:
        return 'Complaint';
      case praise:
        return 'Praise';
      case shippingQuestion:
        return 'Shipping Question';
      case returnRequest:
        return 'Return Request';
      default:
        return 'Unknown';
    }
  }
}

/// Chat message request
class ChatMessageRequest {
  final String message;
  final String? customerIdentifier;
  final String? sessionId;

  ChatMessageRequest({
    required this.message,
    this.customerIdentifier,
    this.sessionId,
  });

  Map<String, dynamic> toJson() {
    return {
      'message': message,
      'customer_identifier': customerIdentifier,
      'session_id': sessionId,
    };
  }
}

/// Chat message response
class ChatMessageResponse {
  final String id;
  final String customerMessage;
  final String aiResponse;
  final List<Map<String, dynamic>> products;
  final String? intentDetected;
  final int responseTimeMs;

  ChatMessageResponse({
    required this.id,
    required this.customerMessage,
    required this.aiResponse,
    this.products = const [],
    this.intentDetected,
    required this.responseTimeMs,
  });

  factory ChatMessageResponse.fromJson(Map<String, dynamic> json) {
    return ChatMessageResponse(
      id: json['id'] as String,
      customerMessage: json['customer_message'] as String,
      aiResponse: json['ai_response'] as String,
      products: (json['products'] as List<dynamic>?)
              ?.map((e) => e as Map<String, dynamic>)
              .toList() ??
          [],
      intentDetected: json['intent_detected'] as String?,
      responseTimeMs: json['response_time_ms'] as int,
    );
  }
}
