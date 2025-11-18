/// Analytics event model for tracking user interactions
class AnalyticsEvent {
  final String id;
  final String userId;
  final String eventType;
  final Map<String, dynamic> eventData;
  final String? sessionId;
  final String? customerIdentifier;
  final String? ipAddress;
  final String? userAgent;
  final DateTime createdAt;

  AnalyticsEvent({
    required this.id,
    required this.userId,
    required this.eventType,
    this.eventData = const {},
    this.sessionId,
    this.customerIdentifier,
    this.ipAddress,
    this.userAgent,
    required this.createdAt,
  });

  factory AnalyticsEvent.fromJson(Map<String, dynamic> json) {
    return AnalyticsEvent(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      eventType: json['event_type'] as String,
      eventData: json['event_data'] as Map<String, dynamic>? ?? {},
      sessionId: json['session_id'] as String?,
      customerIdentifier: json['customer_identifier'] as String?,
      ipAddress: json['ip_address'] as String?,
      userAgent: json['user_agent'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'event_type': eventType,
      'event_data': eventData,
      'session_id': sessionId,
      'customer_identifier': customerIdentifier,
      'ip_address': ipAddress,
      'user_agent': userAgent,
      'created_at': createdAt.toIso8601String(),
    };
  }
}

/// Analytics event types
class EventType {
  static const String questionAsked = 'question_asked';
  static const String productView = 'product_view';
  static const String orderLookup = 'order_lookup';
  static const String conversationStarted = 'conversation_started';
  static const String conversationEnded = 'conversation_ended';
  static const String csvUpload = 'csv_upload';
  static const String settingsUpdated = 'settings_updated';
}

/// Analytics summary for dashboard
class AnalyticsSummary {
  final int totalQuestions;
  final int questionsToday;
  final List<ProductMention> topProducts;
  final List<DailyMetrics> dailyVolume;
  final EngagementMetrics engagement;

  AnalyticsSummary({
    required this.totalQuestions,
    required this.questionsToday,
    required this.topProducts,
    required this.dailyVolume,
    required this.engagement,
  });

  factory AnalyticsSummary.fromJson(Map<String, dynamic> json) {
    return AnalyticsSummary(
      totalQuestions: json['total_questions'] as int,
      questionsToday: json['questions_today'] as int,
      topProducts: (json['top_products'] as List<dynamic>)
          .map((e) => ProductMention.fromJson(e as Map<String, dynamic>))
          .toList(),
      dailyVolume: (json['daily_volume'] as List<dynamic>)
          .map((e) => DailyMetrics.fromJson(e as Map<String, dynamic>))
          .toList(),
      engagement: EngagementMetrics.fromJson(
          json['engagement'] as Map<String, dynamic>),
    );
  }
}

/// Product mention tracking
class ProductMention {
  final String? productId;
  final String productName;
  final int mentionCount;

  ProductMention({
    this.productId,
    required this.productName,
    required this.mentionCount,
  });

  factory ProductMention.fromJson(Map<String, dynamic> json) {
    return ProductMention(
      productId: json['product_id'] as String?,
      productName: json['product_name'] as String,
      mentionCount: json['mention_count'] as int,
    );
  }
}

/// Daily metrics
class DailyMetrics {
  final String date;
  final int eventCount;
  final int? uniqueCustomers;

  DailyMetrics({
    required this.date,
    required this.eventCount,
    this.uniqueCustomers,
  });

  factory DailyMetrics.fromJson(Map<String, dynamic> json) {
    return DailyMetrics(
      date: json['date'] as String,
      eventCount: json['event_count'] as int,
      uniqueCustomers: json['unique_customers'] as int?,
    );
  }
}

/// Engagement metrics
class EngagementMetrics {
  final int totalConversations;
  final int uniqueCustomers;
  final double avgMessagesPerCustomer;
  final int totalEvents;

  EngagementMetrics({
    required this.totalConversations,
    required this.uniqueCustomers,
    required this.avgMessagesPerCustomer,
    required this.totalEvents,
  });

  factory EngagementMetrics.fromJson(Map<String, dynamic> json) {
    return EngagementMetrics(
      totalConversations: json['total_conversations'] as int,
      uniqueCustomers: json['unique_customers'] as int,
      avgMessagesPerCustomer:
          (json['avg_messages_per_customer'] as num).toDouble(),
      totalEvents: json['total_events'] as int,
    );
  }
}

/// Chart data point
class ChartDataPoint {
  final String label;
  final double value;

  ChartDataPoint({
    required this.label,
    required this.value,
  });

  factory ChartDataPoint.fromJson(Map<String, dynamic> json) {
    return ChartDataPoint(
      label: json['date'] as String? ?? json['name'] as String,
      value: (json['count'] as num?)?.toDouble() ??
          (json['value'] as num).toDouble(),
    );
  }
}
