import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../config/constants.dart';
import 'auth_service.dart';
import 'logger_service.dart';

/// Centralized API service for all HTTP requests
/// Handles authentication, error handling, and logging
class ApiService {
  final AuthService _authService;
  final LoggerService _logger;

  ApiService(this._authService, this._logger);

  /// Base headers for all requests
  Future<Map<String, String>> get _baseHeaders async {
    final headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    // Add auth token if available
    final token = await _authService.getToken();
    if (token != null) {
      headers['Authorization'] = 'Bearer $token';
    }

    return headers;
  }

  /// GET request
  Future<ApiResponse> get(
    String endpoint, {
    Map<String, String>? queryParams,
    Duration? timeout,
  }) async {
    try {
      final url = _buildUrl(endpoint, queryParams);
      _logger.logInfo('GET $url');

      final response = await http
          .get(
            url,
            headers: await _baseHeaders,
          )
          .timeout(timeout ?? AppConstants.apiTimeout);

      return _handleResponse(response);
    } on TimeoutException {
      _logger.logError('Request timeout');
      return ApiResponse.error(AppConstants.timeoutError);
    } on http.ClientException catch (e) {
      _logger.logError('HTTP error: ${e.message}');
      return ApiResponse.error(AppConstants.networkError);
    } on SocketException {
      _logger.logError('Network error: No internet connection');
      return ApiResponse.error(AppConstants.networkError);
    } catch (e) {
      _logger.logError('Unexpected error: $e');
      return ApiResponse.error(AppConstants.unknownError);
    }
  }

  /// POST request
  Future<ApiResponse> post(
    String endpoint, {
    Map<String, dynamic>? data,
    Duration? timeout,
  }) async {
    try {
      final url = _buildUrl(endpoint);
      _logger.logInfo('POST $url');

      final response = await http
          .post(
            url,
            headers: await _baseHeaders,
            body: data != null ? jsonEncode(data) : null,
          )
          .timeout(timeout ?? AppConstants.apiTimeout);

      return _handleResponse(response);
    } on TimeoutException {
      _logger.logError('Request timeout');
      return ApiResponse.error(AppConstants.timeoutError);
    } on http.ClientException catch (e) {
      _logger.logError('HTTP error: ${e.message}');
      return ApiResponse.error(AppConstants.networkError);
    } on SocketException {
      _logger.logError('Network error: No internet connection');
      return ApiResponse.error(AppConstants.networkError);
    } catch (e) {
      _logger.logError('Unexpected error: $e');
      return ApiResponse.error(AppConstants.unknownError);
    }
  }

  /// PUT request
  Future<ApiResponse> put(
    String endpoint, {
    Map<String, dynamic>? data,
    Duration? timeout,
  }) async {
    try {
      final url = _buildUrl(endpoint);
      _logger.logInfo('PUT $url');

      final response = await http
          .put(
            url,
            headers: await _baseHeaders,
            body: data != null ? jsonEncode(data) : null,
          )
          .timeout(timeout ?? AppConstants.apiTimeout);

      return _handleResponse(response);
    } on TimeoutException {
      _logger.logError('Request timeout');
      return ApiResponse.error(AppConstants.timeoutError);
    } on http.ClientException catch (e) {
      _logger.logError('HTTP error: ${e.message}');
      return ApiResponse.error(AppConstants.networkError);
    } on SocketException {
      _logger.logError('Network error: No internet connection');
      return ApiResponse.error(AppConstants.networkError);
    } catch (e) {
      _logger.logError('Unexpected error: $e');
      return ApiResponse.error(AppConstants.unknownError);
    }
  }

  /// DELETE request
  Future<ApiResponse> delete(
    String endpoint, {
    Duration? timeout,
  }) async {
    try {
      final url = _buildUrl(endpoint);
      _logger.logInfo('DELETE $url');

      final response = await http
          .delete(
            url,
            headers: await _baseHeaders,
          )
          .timeout(timeout ?? AppConstants.apiTimeout);

      return _handleResponse(response);
    } on TimeoutException {
      _logger.logError('Request timeout');
      return ApiResponse.error(AppConstants.timeoutError);
    } on http.ClientException catch (e) {
      _logger.logError('HTTP error: ${e.message}');
      return ApiResponse.error(AppConstants.networkError);
    } on SocketException {
      _logger.logError('Network error: No internet connection');
      return ApiResponse.error(AppConstants.networkError);
    } catch (e) {
      _logger.logError('Unexpected error: $e');
      return ApiResponse.error(AppConstants.unknownError);
    }
  }

  /// Upload file with multipart request
  Future<ApiResponse> uploadFile(
    String endpoint,
    File file, {
    String fieldName = 'file',
    Map<String, String>? additionalFields,
  }) async {
    try {
      final url = _buildUrl(endpoint);
      _logger.logInfo('POST (multipart) $url');

      final headers = await _baseHeaders;
      headers.remove('Content-Type'); // Let multipart set its own content type

      final request = http.MultipartRequest('POST', url);
      request.headers.addAll(headers);

      // Add file
      request.files.add(await http.MultipartFile.fromPath(
        fieldName,
        file.path,
      ));

      // Add additional fields
      if (additionalFields != null) {
        request.fields.addAll(additionalFields);
      }

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      return _handleResponse(response);
    } on SocketException {
      _logger.logError('Network error: No internet connection');
      return ApiResponse.error(AppConstants.networkError);
    } catch (e) {
      _logger.logError('Upload error: $e');
      return ApiResponse.error(AppConstants.fileUploadError);
    }
  }

  /// Build full URL with query parameters
  Uri _buildUrl(String endpoint, [Map<String, String>? queryParams]) {
    final url = AppConstants.getApiUrl(endpoint);
    final uri = Uri.parse(url);

    if (queryParams != null && queryParams.isNotEmpty) {
      return uri.replace(queryParameters: queryParams);
    }

    return uri;
  }

  /// Handle HTTP response
  ApiResponse _handleResponse(http.Response response) {
    _logger.logInfo(
        'Response ${response.statusCode}: ${response.body.substring(0, 100)}...');

    try {
      final jsonResponse = jsonDecode(response.body) as Map<String, dynamic>;

      if (response.statusCode >= 200 && response.statusCode < 300) {
        return ApiResponse.success(
          data: jsonResponse['data'],
          message: jsonResponse['message'] as String?,
        );
      } else {
        final errorCode = jsonResponse['code'] as String?;
        final errorMessage = jsonResponse['error'] as String? ??
            AppConstants.getErrorMessage(errorCode);

        // Handle auth errors
        if (response.statusCode == 401) {
          _authService.clearAuth();
        }

        return ApiResponse.error(
          errorMessage,
          code: errorCode,
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      _logger.logError('Failed to parse response: $e');
      return ApiResponse.error(
        AppConstants.serverError,
        statusCode: response.statusCode,
      );
    }
  }
}

/// API Response wrapper
class ApiResponse {
  final bool success;
  final dynamic data;
  final String? message;
  final String? errorCode;
  final int? statusCode;

  ApiResponse({
    required this.success,
    this.data,
    this.message,
    this.errorCode,
    this.statusCode,
  });

  factory ApiResponse.success({
    dynamic data,
    String? message,
  }) {
    return ApiResponse(
      success: true,
      data: data,
      message: message,
    );
  }

  factory ApiResponse.error(
    String message, {
    String? code,
    int? statusCode,
  }) {
    return ApiResponse(
      success: false,
      message: message,
      errorCode: code,
      statusCode: statusCode,
    );
  }

  bool get isSuccess => success;
  bool get isError => !success;
}
