
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:scamshield/services/api_service.dart';

void main() {
  test('reports a configured healthy backend', () async {
    final service = ApiService(
      baseUrl: 'http://192.168.1.50:8000/',
      httpGet: (uri) async {
        expect(uri.toString(), 'http://192.168.1.50:8000/health');
        return const ApiResponse(statusCode: 200, body: '{"status":"ok"}');
      },
    );

    expect(await service.checkBackendHealth(), isTrue);
  });

  test('reports an unconfigured backend without making a request', () async {
    final service = ApiService(
      baseUrl: '',
      httpGet: (_) => throw StateError('A request should not be made.'),
    );

    final health = await service.checkBackendHealthDetails();
    expect(health.isConnected, isFalse);
    expect(health.message, contains('not configured'));
  });

  test('handles timeouts, connection failures, and invalid responses', () async {
    final timeoutService = ApiService(
      baseUrl: 'http://192.168.1.50:8000',
      timeout: const Duration(milliseconds: 1),
      httpGet: (_) => Future<ApiResponse>.delayed(
        const Duration(seconds: 1),
        () => const ApiResponse(statusCode: 200, body: '{"status":"ok"}'),
      ),
    );
    expect((await timeoutService.checkBackendHealthDetails()).message,
        contains('timed out'));

    final connectionService = ApiService(
      baseUrl: 'http://192.168.1.50:8000',
      httpGet: (_) => Future<ApiResponse>.error(const SocketException('refused')),
    );
    expect((await connectionService.checkBackendHealthDetails()).message,
        contains('Could not reach'));

    final invalidResponseService = ApiService(
      baseUrl: 'http://192.168.1.50:8000',
      httpGet: (_) async => const ApiResponse(statusCode: 200, body: '{}'),
    );
    expect((await invalidResponseService.checkBackendHealthDetails()).message,
        contains('unexpected'));
  });
}
