/// Order item model representing individual items in an order
class OrderItem {
  final String? productId;
  final String productName;
  final int quantity;
  final double price;

  OrderItem({
    this.productId,
    required this.productName,
    required this.quantity,
    required this.price,
  });

  factory OrderItem.fromJson(Map<String, dynamic> json) {
    return OrderItem(
      productId: json['product_id'] as String?,
      productName: json['product_name'] as String,
      quantity: json['quantity'] as int,
      price: (json['price'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'product_id': productId,
      'product_name': productName,
      'quantity': quantity,
      'price': price,
    };
  }

  /// Calculate subtotal for this item
  double get subtotal => price * quantity;

  OrderItem copyWith({
    String? productId,
    String? productName,
    int? quantity,
    double? price,
  }) {
    return OrderItem(
      productId: productId ?? this.productId,
      productName: productName ?? this.productName,
      quantity: quantity ?? this.quantity,
      price: price ?? this.price,
    );
  }

  @override
  String toString() {
    return 'OrderItem(name: $productName, quantity: $quantity, price: \$$price)';
  }
}
