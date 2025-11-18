import 'order_item.dart';

/// Order model representing customer orders
class Order {
  final String id;
  final String userId;
  final String orderId;
  final String customerEmail;
  final String? customerName;
  final String? customerPhone;
  final List<OrderItem> items;
  final double subtotal;
  final double tax;
  final double shipping;
  final double total;
  final String status;
  final String paymentStatus;
  final Map<String, dynamic>? shippingAddress;
  final Map<String, dynamic>? billingAddress;
  final DateTime? estimatedDelivery;
  final DateTime? actualDelivery;
  final String? trackingNumber;
  final String? trackingUrl;
  final String? notes;
  final DateTime createdAt;
  final DateTime? updatedAt;

  Order({
    required this.id,
    required this.userId,
    required this.orderId,
    required this.customerEmail,
    this.customerName,
    this.customerPhone,
    required this.items,
    required this.subtotal,
    this.tax = 0.0,
    this.shipping = 0.0,
    required this.total,
    required this.status,
    this.paymentStatus = 'pending',
    this.shippingAddress,
    this.billingAddress,
    this.estimatedDelivery,
    this.actualDelivery,
    this.trackingNumber,
    this.trackingUrl,
    this.notes,
    required this.createdAt,
    this.updatedAt,
  });

  factory Order.fromJson(Map<String, dynamic> json) {
    return Order(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      orderId: json['order_id'] as String,
      customerEmail: json['customer_email'] as String,
      customerName: json['customer_name'] as String?,
      customerPhone: json['customer_phone'] as String?,
      items: (json['items'] as List<dynamic>)
          .map((e) => OrderItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      subtotal: (json['subtotal'] as num).toDouble(),
      tax: (json['tax'] as num?)?.toDouble() ?? 0.0,
      shipping: (json['shipping'] as num?)?.toDouble() ?? 0.0,
      total: (json['total'] as num).toDouble(),
      status: json['status'] as String,
      paymentStatus: json['payment_status'] as String? ?? 'pending',
      shippingAddress: json['shipping_address'] as Map<String, dynamic>?,
      billingAddress: json['billing_address'] as Map<String, dynamic>?,
      estimatedDelivery: json['estimated_delivery'] != null
          ? DateTime.parse(json['estimated_delivery'] as String)
          : null,
      actualDelivery: json['actual_delivery'] != null
          ? DateTime.parse(json['actual_delivery'] as String)
          : null,
      trackingNumber: json['tracking_number'] as String?,
      trackingUrl: json['tracking_url'] as String?,
      notes: json['notes'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'order_id': orderId,
      'customer_email': customerEmail,
      'customer_name': customerName,
      'customer_phone': customerPhone,
      'items': items.map((e) => e.toJson()).toList(),
      'subtotal': subtotal,
      'tax': tax,
      'shipping': shipping,
      'total': total,
      'status': status,
      'payment_status': paymentStatus,
      'shipping_address': shippingAddress,
      'billing_address': billingAddress,
      'estimated_delivery': estimatedDelivery?.toIso8601String(),
      'actual_delivery': actualDelivery?.toIso8601String(),
      'tracking_number': trackingNumber,
      'tracking_url': trackingUrl,
      'notes': notes,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
    };
  }

  /// Convert to status card format for chat display
  Map<String, dynamic> toStatusCardJson() {
    return {
      'id': id,
      'order_id': orderId,
      'customer_email': customerEmail,
      'customer_name': customerName,
      'items': items.map((e) => e.toJson()).toList(),
      'total': total,
      'status': status,
      'status_color': OrderStatus.getColor(status),
      'estimated_delivery': estimatedDelivery?.toIso8601String(),
      'tracking_number': trackingNumber,
      'created_at': createdAt.toIso8601String(),
    };
  }

  Order copyWith({
    String? id,
    String? userId,
    String? orderId,
    String? customerEmail,
    String? customerName,
    String? customerPhone,
    List<OrderItem>? items,
    double? subtotal,
    double? tax,
    double? shipping,
    double? total,
    String? status,
    String? paymentStatus,
    Map<String, dynamic>? shippingAddress,
    Map<String, dynamic>? billingAddress,
    DateTime? estimatedDelivery,
    DateTime? actualDelivery,
    String? trackingNumber,
    String? trackingUrl,
    String? notes,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Order(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      orderId: orderId ?? this.orderId,
      customerEmail: customerEmail ?? this.customerEmail,
      customerName: customerName ?? this.customerName,
      customerPhone: customerPhone ?? this.customerPhone,
      items: items ?? this.items,
      subtotal: subtotal ?? this.subtotal,
      tax: tax ?? this.tax,
      shipping: shipping ?? this.shipping,
      total: total ?? this.total,
      status: status ?? this.status,
      paymentStatus: paymentStatus ?? this.paymentStatus,
      shippingAddress: shippingAddress ?? this.shippingAddress,
      billingAddress: billingAddress ?? this.billingAddress,
      estimatedDelivery: estimatedDelivery ?? this.estimatedDelivery,
      actualDelivery: actualDelivery ?? this.actualDelivery,
      trackingNumber: trackingNumber ?? this.trackingNumber,
      trackingUrl: trackingUrl ?? this.trackingUrl,
      notes: notes ?? this.notes,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  String toString() {
    return 'Order(orderId: $orderId, total: \$$total, status: $status)';
  }
}

/// Order status constants and helpers
class OrderStatus {
  static const String pending = 'pending';
  static const String processing = 'processing';
  static const String shipped = 'shipped';
  static const String inTransit = 'in_transit';
  static const String outForDelivery = 'out_for_delivery';
  static const String delivered = 'delivered';
  static const String cancelled = 'cancelled';
  static const String refunded = 'refunded';
  static const String failed = 'failed';

  /// Get color hex for status
  static String getColor(String status) {
    switch (status.toLowerCase()) {
      case pending:
      case processing:
        return '#FBC02D'; // Yellow
      case shipped:
      case inTransit:
      case outForDelivery:
        return '#2196F3'; // Blue
      case delivered:
        return '#4CAF50'; // Green
      case cancelled:
      case refunded:
      case failed:
        return '#F44336'; // Red
      default:
        return '#999999'; // Gray
    }
  }

  /// Get display name for status
  static String getDisplayName(String status) {
    switch (status.toLowerCase()) {
      case pending:
        return 'Pending';
      case processing:
        return 'Processing';
      case shipped:
        return 'Shipped';
      case inTransit:
        return 'In Transit';
      case outForDelivery:
        return 'Out for Delivery';
      case delivered:
        return 'Delivered';
      case cancelled:
        return 'Cancelled';
      case refunded:
        return 'Refunded';
      case failed:
        return 'Failed';
      default:
        return status;
    }
  }
}
