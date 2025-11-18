import 'package:get/get.dart';
import 'package:flutter/material.dart';

/// Application routes configuration using GetX
/// Defines all named routes and their corresponding pages
class AppRoutes {
  // ==========================================
  // Route Names
  // ==========================================

  /// Splash screen (initial route)
  static const String splash = '/';

  // Authentication routes
  static const String login = '/login';
  static const String signup = '/signup';
  static const String resetPassword = '/reset-password';

  // Customer routes
  static const String customerChat = '/customer/chat';
  static const String customerOrder = '/customer/order';
  static const String customerSettings = '/customer/settings';

  // Owner/Admin routes
  static const String ownerDashboard = '/owner/dashboard';
  static const String ownerProducts = '/owner/products';
  static const String ownerProductUpload = '/owner/products/upload';
  static const String ownerAnalytics = '/owner/analytics';
  static const String ownerSettings = '/owner/settings';

  // Shared routes
  static const String orderDetails = '/order/:orderId';
  static const String productDetails = '/product/:productId';

  // ==========================================
  // Route Pages
  // ==========================================

  static List<GetPage> get pages {
    return [
      // Note: Pages will be imported when created
      // For now, this shows the structure

      // GetPage(
      //   name: splash,
      //   page: () => const SplashPage(),
      // ),

      // GetPage(
      //   name: login,
      //   page: () => const LoginPage(),
      //   transition: Transition.fadeIn,
      // ),

      // GetPage(
      //   name: signup,
      //   page: () => const SignupPage(),
      //   transition: Transition.rightToLeft,
      // ),

      // GetPage(
      //   name: resetPassword,
      //   page: () => const ResetPasswordPage(),
      //   transition: Transition.rightToLeft,
      // ),

      // GetPage(
      //   name: customerChat,
      //   page: () => const ChatPage(),
      //   transition: Transition.fadeIn,
      // ),

      // GetPage(
      //   name: customerOrder,
      //   page: () => const OrderPage(),
      //   transition: Transition.rightToLeft,
      // ),

      // GetPage(
      //   name: customerSettings,
      //   page: () => const CustomerSettingsPage(),
      //   transition: Transition.rightToLeft,
      // ),

      // GetPage(
      //   name: ownerDashboard,
      //   page: () => const DashboardPage(),
      //   transition: Transition.fadeIn,
      // ),

      // GetPage(
      //   name: ownerProducts,
      //   page: () => const ProductsPage(),
      //   transition: Transition.rightToLeft,
      // ),

      // GetPage(
      //   name: ownerProductUpload,
      //   page: () => const ProductUploadPage(),
      //   transition: Transition.rightToLeft,
      // ),

      // GetPage(
      //   name: ownerAnalytics,
      //   page: () => const AnalyticsPage(),
      //   transition: Transition.rightToLeft,
      // ),

      // GetPage(
      //   name: ownerSettings,
      //   page: () => const OwnerSettingsPage(),
      //   transition: Transition.rightToLeft,
      // ),

      // GetPage(
      //   name: orderDetails,
      //   page: () => const OrderDetailsPage(),
      //   transition: Transition.rightToLeft,
      // ),

      // GetPage(
      //   name: productDetails,
      //   page: () => const ProductDetailsPage(),
      //   transition: Transition.rightToLeft,
      // ),
    ];
  }

  // ==========================================
  // Navigation Helper Methods
  // ==========================================

  /// Navigate to login page
  static void toLogin() {
    Get.offAllNamed(login);
  }

  /// Navigate to signup page
  static void toSignup() {
    Get.toNamed(signup);
  }

  /// Navigate to customer chat page
  static void toCustomerChat() {
    Get.offAllNamed(customerChat);
  }

  /// Navigate to owner dashboard
  static void toOwnerDashboard() {
    Get.offAllNamed(ownerDashboard);
  }

  /// Navigate to order details
  static void toOrderDetails(String orderId) {
    Get.toNamed(
      orderDetails.replaceAll(':orderId', orderId),
      arguments: {'orderId': orderId},
    );
  }

  /// Navigate to product details
  static void toProductDetails(String productId) {
    Get.toNamed(
      productDetails.replaceAll(':productId', productId),
      arguments: {'productId': productId},
    );
  }

  /// Navigate back
  static void back() {
    Get.back();
  }

  /// Navigate to previous page until condition
  static void backUntil(bool Function(Route<dynamic>) predicate) {
    Get.until(predicate);
  }

  /// Close all dialogs and bottom sheets
  static void closeAllDialogs() {
    if (Get.isDialogOpen ?? false) {
      Get.back();
    }
    if (Get.isBottomSheetOpen ?? false) {
      Get.back();
    }
  }

  // ==========================================
  // Dialog & Bottom Sheet Helpers
  // ==========================================

  /// Show error dialog
  static Future<void> showErrorDialog({
    required String title,
    required String message,
    String? buttonText,
  }) {
    return Get.dialog(
      // ErrorDialog widget will be created in widgets
      Container(), // Placeholder
      barrierDismissible: false,
    );
  }

  /// Show success dialog
  static Future<void> showSuccessDialog({
    required String title,
    required String message,
    String? buttonText,
  }) {
    return Get.dialog(
      // SuccessDialog widget will be created in widgets
      Container(), // Placeholder
      barrierDismissible: true,
    );
  }

  /// Show loading dialog
  static void showLoadingDialog([String? message]) {
    Get.dialog(
      // LoadingDialog widget will be created in widgets
      Container(), // Placeholder
      barrierDismissible: false,
    );
  }

  /// Hide loading dialog
  static void hideLoadingDialog() {
    if (Get.isDialogOpen ?? false) {
      Get.back();
    }
  }

  /// Show bottom sheet
  static Future<T?> showAppBottomSheet<T>(Widget child) {
    return Get.bottomSheet<T>(
      child,
      backgroundColor: Get.theme.scaffoldBackgroundColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(
          top: Radius.circular(16),
        ),
      ),
      isScrollControlled: true,
    );
  }

  /// Show snackbar
  static void showSnackbar({
    required String title,
    required String message,
    bool isError = false,
  }) {
    Get.snackbar(
      title,
      message,
      snackPosition: SnackPosition.BOTTOM,
      backgroundColor:
          isError ? Get.theme.colorScheme.error : Get.theme.colorScheme.primary,
      colorText: Get.theme.colorScheme.onPrimary,
      margin: const EdgeInsets.all(16),
      borderRadius: 8,
      duration: const Duration(seconds: 3),
    );
  }
}
