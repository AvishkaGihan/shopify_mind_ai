/// Store colors configuration
class StoreColors {
  final String primary;
  final String accent;
  final String supporting;

  StoreColors({
    required this.primary,
    required this.accent,
    required this.supporting,
  });

  factory StoreColors.fromJson(Map<String, dynamic> json) {
    return StoreColors(
      primary: json['primary'] as String? ?? '#00a86b',
      accent: json['accent'] as String? ?? '#f97316',
      supporting: json['supporting'] as String? ?? '#a78bfa',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'primary': primary,
      'accent': accent,
      'supporting': supporting,
    };
  }

  StoreColors copyWith({
    String? primary,
    String? accent,
    String? supporting,
  }) {
    return StoreColors(
      primary: primary ?? this.primary,
      accent: accent ?? this.accent,
      supporting: supporting ?? this.supporting,
    );
  }
}

/// User model representing a store owner
class User {
  final String id;
  final String email;
  final String? storeName;
  final StoreColors storeColors;
  final String aiTone;
  final bool isActive;
  final bool isVerified;
  final DateTime? createdAt;
  final DateTime? updatedAt;
  final DateTime? lastLoginAt;

  User({
    required this.id,
    required this.email,
    this.storeName,
    required this.storeColors,
    required this.aiTone,
    this.isActive = true,
    this.isVerified = false,
    this.createdAt,
    this.updatedAt,
    this.lastLoginAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      email: json['email'] as String,
      storeName: json['store_name'] as String?,
      storeColors: json['store_colors'] != null
          ? StoreColors.fromJson(json['store_colors'] as Map<String, dynamic>)
          : StoreColors(
              primary: '#00a86b',
              accent: '#f97316',
              supporting: '#a78bfa',
            ),
      aiTone: json['ai_tone'] as String? ?? 'friendly',
      isActive: json['is_active'] as bool? ?? true,
      isVerified: json['is_verified'] as bool? ?? false,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : null,
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : null,
      lastLoginAt: json['last_login_at'] != null
          ? DateTime.parse(json['last_login_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'store_name': storeName,
      'store_colors': storeColors.toJson(),
      'ai_tone': aiTone,
      'is_active': isActive,
      'is_verified': isVerified,
      'created_at': createdAt?.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
      'last_login_at': lastLoginAt?.toIso8601String(),
    };
  }

  User copyWith({
    String? id,
    String? email,
    String? storeName,
    StoreColors? storeColors,
    String? aiTone,
    bool? isActive,
    bool? isVerified,
    DateTime? createdAt,
    DateTime? updatedAt,
    DateTime? lastLoginAt,
  }) {
    return User(
      id: id ?? this.id,
      email: email ?? this.email,
      storeName: storeName ?? this.storeName,
      storeColors: storeColors ?? this.storeColors,
      aiTone: aiTone ?? this.aiTone,
      isActive: isActive ?? this.isActive,
      isVerified: isVerified ?? this.isVerified,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      lastLoginAt: lastLoginAt ?? this.lastLoginAt,
    );
  }

  @override
  String toString() {
    return 'User(id: $id, email: $email, storeName: $storeName)';
  }
}

/// Authentication response from login/signup
class AuthResponse {
  final String userId;
  final String email;
  final String? storeName;
  final String token;
  final int expiresIn;

  AuthResponse({
    required this.userId,
    required this.email,
    this.storeName,
    required this.token,
    required this.expiresIn,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      userId: json['user_id'] as String,
      email: json['email'] as String,
      storeName: json['store_name'] as String?,
      token: json['token'] as String,
      expiresIn: json['expires_in'] as int,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'email': email,
      'store_name': storeName,
      'token': token,
      'expires_in': expiresIn,
    };
  }
}
