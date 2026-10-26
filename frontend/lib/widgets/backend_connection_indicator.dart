import 'package:flutter/material.dart';

import '../services/api_service.dart';

class BackendConnectionIndicator extends StatefulWidget {
  const BackendConnectionIndicator({super.key, this.apiService});

  final ApiService? apiService;

  @override
  State<BackendConnectionIndicator> createState() =>
      _BackendConnectionIndicatorState();
}

class _BackendConnectionIndicatorState
    extends State<BackendConnectionIndicator> {
  late final ApiService _apiService = widget.apiService ?? ApiService();
  _ConnectionState _connectionState = _ConnectionState.idle;
  String _message = 'Test the connection before using backend features.';

  Future<void> _testConnection() async {
    setState(() => _connectionState = _ConnectionState.connecting);
    final health = await _apiService.checkBackendHealthDetails();
    if (!mounted) {
      return;
    }
    setState(() {
      _connectionState = health.isConnected
          ? _ConnectionState.connected
          : _ConnectionState.offline;
      _message = health.message;
    });
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(health.message)));
  }

  @override
  Widget build(BuildContext context) {
    final isConnecting = _connectionState == _ConnectionState.connecting;
    final isConnected = _connectionState == _ConnectionState.connected;
    final isOffline = _connectionState == _ConnectionState.offline;
    final color = isConnected
        ? const Color(0xFF6EE7B7)
        : isOffline
            ? const Color(0xFFFCA5A5)
            : const Color(0xFFB6C2D4);
    final icon = isConnected
        ? Icons.cloud_done_outlined
        : isOffline
            ? Icons.cloud_off_outlined
            : Icons.cloud_outlined;
    final label = isConnecting
        ? 'Connecting...'
        : isConnected
            ? 'Backend Connected'
            : isOffline
                ? 'Backend Offline'
                : 'Backend status';

    return Container(
      padding: const EdgeInsets.fromLTRB(14, 10, 8, 10),
      decoration: BoxDecoration(
        color: const Color(0xFF0D1524),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF273449)),
      ),
      child: Row(
        children: [
          Icon(icon, size: 20, color: color),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: TextStyle(color: color, fontWeight: FontWeight.w700)),
                const SizedBox(height: 2),
                Text(
                  _message,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(color: Color(0xFF9AA9BF), fontSize: 12),
                ),
              ],
            ),
          ),
          TextButton(
            onPressed: isConnecting ? null : _testConnection,
            child: Text(isConnecting ? 'Checking' : 'Test'),
          ),
        ],
      ),
    );
  }
}

enum _ConnectionState { idle, connecting, connected, offline }
