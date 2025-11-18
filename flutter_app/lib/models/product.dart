/// Product model representing inventory items
class Product {
  final String id;
  final String userId;
  final String name;
  final String? description;
  final double price;
  final String? category;
  final String? sku;
  final String? imageUrl;
  final int stockQuantity;
  final bool isActive;
  final Map<String, dynamic>? metadata;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  Product({
    required this.id,
    required this.userId,
    required this.name,
    this.description,
    required this.price,
    this.category,
    this.sku,
    this.imageUrl,
    this.stockQuantity = 0,
    this.isActive = true,
    this.metadata,
    this.createdAt,
    this.updatedAt,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      price: (json['price'] as num).toDouble(),
      category: json['category'] as String?,
      sku: json['sku'] as String?,
      imageUrl: json['image_url'] as String?,
      stockQuantity: json['stock_quantity'] as int? ?? 0,
      isActive: json['is_active'] as bool? ?? true,
      metadata: json['metadata'] as Map<String, dynamic>?,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : null,
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'name': name,
      'description': description,
      'price': price,
      'category': category,
      'sku': sku,
      'image_url': imageUrl,
      'stock_quantity': stockQuantity,
      'is_active': isActive,
      'metadata': metadata,
      'created_at': createdAt?.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
    };
  }

  /// Convert to card format for chat display
  Map<String, dynamic> toCardJson() {
    return {
      'id': id,
      'name': name,
      'description': description != null && description!.length > 200
          ? '${description!.substring(0, 200)}...'
          : description,
      'price': price,
      'category': category,
      'image_url': imageUrl,
    };
  }

  Product copyWith({
    String? id,
    String? userId,
    String? name,
    String? description,
    double? price,
    String? category,
    String? sku,
    String? imageUrl,
    int? stockQuantity,
    bool? isActive,
    Map<String, dynamic>? metadata,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Product(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      name: name ?? this.name,
      description: description ?? this.description,
      price: price ?? this.price,
      category: category ?? this.category,
      sku: sku ?? this.sku,
      imageUrl: imageUrl ?? this.imageUrl,
      stockQuantity: stockQuantity ?? this.stockQuantity,
      isActive: isActive ?? this.isActive,
      metadata: metadata ?? this.metadata,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  String toString() {
    return 'Product(id: $id, name: $name, price: \$$price)';
  }
}

/// Product upload response
class ProductUploadResponse {
  final int totalRows;
  final int inserted;
  final int failed;
  final List<ProductUploadError> errors;

  ProductUploadResponse({
    required this.totalRows,
    required this.inserted,
    required this.failed,
    required this.errors,
  });

  factory ProductUploadResponse.fromJson(Map<String, dynamic> json) {
    return ProductUploadResponse(
      totalRows: json['total_rows'] as int,
      inserted: json['inserted'] as int,
      failed: json['failed'] as int,
      errors: (json['errors'] as List<dynamic>?)
              ?.map(
                  (e) => ProductUploadError.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }

  bool get hasErrors => failed > 0;
  bool get isPartialSuccess => inserted > 0 && failed > 0;
  bool get isFullSuccess => inserted > 0 && failed == 0;
}

/// Product upload error details
class ProductUploadError {
  final int row;
  final String error;
  final Map<String, dynamic>? data;

  ProductUploadError({
    required this.row,
    required this.error,
    this.data,
  });

  factory ProductUploadError.fromJson(Map<String, dynamic> json) {
    return ProductUploadError(
      row: json['row'] as int,
      error: json['error'] as String,
      data: json['data'] as Map<String, dynamic>?,
    );
  }

  @override
  String toString() {
    return 'Row $row: $error';
  }
}
