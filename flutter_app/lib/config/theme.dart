import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// App theme configuration with Emerald color scheme
/// Based on UX Design Specification
class AppTheme {
  // ==========================================
  // Emerald Color System
  // ==========================================

  /// Primary emerald color
  static const Color primaryEmerald = Color(0xFF00A86B);

  /// Bright emerald for accents and highlights
  static const Color brightEmerald = Color(0xFF00D084);

  /// Deep emerald for text and darker elements
  static const Color deepEmerald = Color(0xFF047857);

  // ==========================================
  // Semantic Colors
  // ==========================================

  /// Success color (emerald variant)
  static const Color success = Color(0xFF047857);

  /// Warning color (amber)
  static const Color warning = Color(0xFFF59E0B);

  /// Error color (red)
  static const Color error = Color(0xFFEF4444);

  // ==========================================
  // Neutral Colors
  // ==========================================

  /// Background light color
  static const Color backgroundLight = Color(0xFFF0FDF4);

  /// Border color
  static const Color border = Color(0xFFD1FAE5);

  /// Text primary (dark gray)
  static const Color textPrimary = Color(0xFF1F2937);

  /// Text secondary (medium gray)
  static const Color textSecondary = Color(0xFF6B7280);

  /// Text tertiary (light gray)
  static const Color textTertiary = Color(0xFF999999);

  // ==========================================
  // Order Status Colors
  // ==========================================

  /// Pending/Processing status (yellow)
  static const Color statusPending = Color(0xFFFBC02D);

  /// Shipped/In Transit status (blue)
  static const Color statusShipped = Color(0xFF2196F3);

  /// Delivered status (green)
  static const Color statusDelivered = Color(0xFF4CAF50);

  /// Cancelled/Error status (red)
  static const Color statusCancelled = Color(0xFFF44336);

  // ==========================================
  // Typography
  // ==========================================

  /// Display text style (32px, bold)
  static const TextStyle displayStyle = TextStyle(
    fontSize: 32,
    fontWeight: FontWeight.w700,
    fontFamily: 'Poppins',
    height: 1.2,
    color: textPrimary,
  );

  /// Heading 1 text style (24px, bold)
  static const TextStyle heading1Style = TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.w700,
    fontFamily: 'Poppins',
    height: 1.2,
    color: textPrimary,
  );

  /// Heading 2 text style (20px, bold)
  static const TextStyle heading2Style = TextStyle(
    fontSize: 20,
    fontWeight: FontWeight.w700,
    fontFamily: 'Poppins',
    height: 1.2,
    color: textPrimary,
  );

  /// Body large text style (16px, medium)
  static const TextStyle bodyLargeStyle = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w500,
    fontFamily: 'Inter',
    height: 1.5,
    color: textPrimary,
  );

  /// Body text style (14px, regular)
  static const TextStyle bodyStyle = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.w400,
    fontFamily: 'Inter',
    height: 1.5,
    color: textPrimary,
  );

  /// Body small text style (13px, regular)
  static const TextStyle bodySmallStyle = TextStyle(
    fontSize: 13,
    fontWeight: FontWeight.w400,
    fontFamily: 'Inter',
    height: 1.5,
    color: textSecondary,
  );

  /// Label text style (12px, semibold)
  static const TextStyle labelStyle = TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.w600,
    fontFamily: 'Inter',
    height: 1.4,
    color: textSecondary,
  );

  /// Caption text style (11px, medium)
  static const TextStyle captionStyle = TextStyle(
    fontSize: 11,
    fontWeight: FontWeight.w500,
    fontFamily: 'Inter',
    height: 1.4,
    color: textTertiary,
  );

  // ==========================================
  // Spacing System (Base unit: 4px)
  // ==========================================

  static const double spacingXs = 4.0;
  static const double spacingSm = 8.0;
  static const double spacingMd = 12.0;
  static const double spacingLg = 16.0;
  static const double spacingXl = 20.0;
  static const double spacing2Xl = 24.0;
  static const double spacing3Xl = 32.0;
  static const double spacing4Xl = 40.0;

  // ==========================================
  // Border Radius
  // ==========================================

  static const double radiusSmall = 8.0;
  static const double radiusMedium = 12.0;
  static const double radiusLarge = 16.0;
  static const double radiusPill = 20.0;

  // ==========================================
  // Light Theme
  // ==========================================

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      primaryColor: primaryEmerald,
      scaffoldBackgroundColor: Colors.white,
      colorScheme: const ColorScheme.light(
        primary: primaryEmerald,
        secondary: brightEmerald,
        error: error,
        surface: backgroundLight,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onError: Colors.white,
        onSurface: textPrimary,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: primaryEmerald,
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: false,
        systemOverlayStyle: SystemUiOverlayStyle.light,
        titleTextStyle: heading2Style.copyWith(color: Colors.white),
      ),
      textTheme: const TextTheme(
        displayLarge: displayStyle,
        headlineLarge: heading1Style,
        headlineMedium: heading2Style,
        bodyLarge: bodyLargeStyle,
        bodyMedium: bodyStyle,
        bodySmall: bodySmallStyle,
        labelLarge: labelStyle,
        labelSmall: captionStyle,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryEmerald,
          foregroundColor: Colors.white,
          minimumSize: const Size(double.infinity, 44),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(radiusSmall),
          ),
          textStyle: bodyLargeStyle.copyWith(
            fontWeight: FontWeight.w600,
            color: Colors.white,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: primaryEmerald,
          minimumSize: const Size(double.infinity, 44),
          side: const BorderSide(color: primaryEmerald),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(radiusSmall),
          ),
          textStyle: bodyLargeStyle.copyWith(
            fontWeight: FontWeight.w600,
            color: primaryEmerald,
          ),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: primaryEmerald,
          textStyle: bodyLargeStyle.copyWith(
            fontWeight: FontWeight.w600,
            color: primaryEmerald,
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: backgroundLight,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusPill),
          borderSide: const BorderSide(color: border),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusPill),
          borderSide: const BorderSide(color: border),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusPill),
          borderSide: const BorderSide(color: primaryEmerald, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusPill),
          borderSide: const BorderSide(color: error),
        ),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: spacingLg,
          vertical: spacingMd,
        ),
        hintStyle: bodyStyle.copyWith(color: textTertiary),
      ),
      cardTheme: CardThemeData(
        color: Colors.white,
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(radiusMedium),
          side: const BorderSide(color: border),
        ),
        margin: const EdgeInsets.all(0),
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        selectedItemColor: primaryEmerald,
        unselectedItemColor: textTertiary,
        showUnselectedLabels: true,
        type: BottomNavigationBarType.fixed,
        elevation: 8,
      ),
    );
  }

  // ==========================================
  // Helper Methods
  // ==========================================

  /// Get color for order status
  static Color getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
      case 'processing':
        return statusPending;
      case 'shipped':
      case 'in_transit':
      case 'out_for_delivery':
        return statusShipped;
      case 'delivered':
        return statusDelivered;
      case 'cancelled':
      case 'refunded':
      case 'failed':
        return statusCancelled;
      default:
        return textTertiary;
    }
  }

  /// Create a gradient background
  static LinearGradient get emeraldGradient {
    return const LinearGradient(
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
      colors: [brightEmerald, primaryEmerald],
    );
  }

  /// Create a box shadow
  static List<BoxShadow> get cardShadow {
    return [
      BoxShadow(
        color: Colors.black.withValues(alpha: 0.08),
        blurRadius: 8,
        offset: const Offset(0, 2),
      ),
    ];
  }

  /// Create a prominent box shadow
  static List<BoxShadow> get prominentShadow {
    return [
      BoxShadow(
        color: Colors.black.withValues(alpha: 0.12),
        blurRadius: 12,
        offset: const Offset(0, 4),
      ),
    ];
  }
}
