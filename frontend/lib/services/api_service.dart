
import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

typedef HttpGet = Future<ApiResponse> Function(Uri uri);

class ApiResponse {
  const ApiResponse({
    required this.statusCode,
    this.body = '',
  });

  final int statusCode;
  final String body;
}

class BackendHealth {
  const BackendHealth({
    required this.isConnected,
    required this.message,
  });

  final bool isConnected;
  final String message;
}

class ApiService {
  ApiService({
    String? baseUrl,
    HttpGet? httpGet,
    Duration timeout = const Duration(seconds: 8),
    http.Client? client,
  })  : baseUrl = (baseUrl ??
                const String.fromEnvironment(
                  'BACKEND_BASE_URL',
                  defaultValue: 'http://10.0.2.2:8000',
                ))
            .replaceAll(RegExp(r'/$'), ''),
        _httpGet = httpGet,
        _timeout = timeout,
        _client = client ?? http.Client();

  final String baseUrl;
  final HttpGet? _httpGet;
  final Duration _timeout;
  final http.Client _client;

  Future<ApiResponse> _get(Uri uri) async {
    if (_httpGet != null) {
      return _httpGet(uri).timeout(_timeout);
    }

    final response = await _client.get(uri).timeout(_timeout);
    return ApiResponse(
      statusCode: response.statusCode,
      body: response.body,
    );
  }

  Future<BackendHealth> checkBackendHealthDetails() async {
    try {
      final response = await _get(Uri.parse('$baseUrl/health'));

      if (response.statusCode == 200) {
        return const BackendHealth(
          isConnected: true,
          message: 'Connected to ScamShield API.',
        );
      }

      return BackendHealth(
        isConnected: false,
        message: 'Backend returned HTTP ${response.statusCode}.',
      );
    } catch (_) {
      return const BackendHealth(
        isConnected: false,
        message: 'Cannot reach backend. Check Wi-Fi and server status.',
      );
    }
  }

  Future<bool> checkBackendHealth() async {
    final result = await checkBackendHealthDetails();
    return result.isConnected;
  }

  Future<Map<String, dynamic>> analyze({
    String? message,
    String? url,
  }) async {
    final body = <String, dynamic>{};

    if (message != null && message.trim().isNotEmpty) {
      body['message'] = message.trim();
    }
    if (url != null && url.trim().isNotEmpty) {
      body['url'] = url.trim();
    }

    if (body.isEmpty) {
      throw ArgumentError('Enter a message or URL to analyze.');
    }

    final response = await _client
        .post(
          Uri.parse('$baseUrl/api/v1/analyze'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode(body),
        )
        .timeout(const Duration(seconds: 30));

    final decoded = jsonDecode(response.body);

    if (response.statusCode != 200) {
      final detail = decoded is Map ? decoded['detail'] : null;
      throw Exception(detail?.toString() ?? 'Analysis failed.');
    }

    if (decoded is! Map<String, dynamic>) {
      throw const FormatException('Unexpected backend response.');
    }

    return decoded;
  }

  void dispose() {
    _client.close();
  }
}
