
import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../widgets/analysis_card.dart';
import '../widgets/backend_connection_indicator.dart';
import '../widgets/recent_checks.dart';
import '../widgets/safety_tips.dart';
import '../widgets/scamshield_header.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _messageController = TextEditingController();
  final _urlController = TextEditingController();
  final _apiService = ApiService();

  bool _isAnalyzing = false;
  Map<String, dynamic>? _result;
  String? _errorMessage;

  @override
  void dispose() {
    _messageController.dispose();
    _urlController.dispose();
    _apiService.dispose();
    super.dispose();
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(message)));
  }

  Future<void> _scan() async {
    final message = _messageController.text.trim();
    final url = _urlController.text.trim();

    if (message.isEmpty && url.isEmpty) {
      _showMessage('Enter a message or URL to analyze.');
      return;
    }

    setState(() {
      _isAnalyzing = true;
      _result = null;
      _errorMessage = null;
    });

    try {
      final result = await _apiService.analyze(
        message: message.isEmpty ? null : message,
        url: url.isEmpty ? null : url,
      );

      if (!mounted) return;

      setState(() {
        _result = result;
        _isAnalyzing = false;
      });
    } catch (error) {
      if (!mounted) return;

      setState(() {
        _isAnalyzing = false;
        _errorMessage =
            'Analysis failed. Check your connection and try again.';
      });
    }
  }

  @override
  Widget build(BuildContext context) => LayoutBuilder(
        builder: (context, constraints) => SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(20, 24, 20, 32),
          child: Center(
            child: ConstrainedBox(
              constraints: BoxConstraints(
                maxWidth: constraints.maxWidth > 700 ? 640 : 560,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const ScamShieldHeader(),
                  const SizedBox(height: 18),
                  const BackendConnectionIndicator(),
                  const SizedBox(height: 28),
                  Text(
                    'Check before\nyou trust.',
                    style: Theme.of(context)
                        .textTheme
                        .displaySmall
                        ?.copyWith(
                          fontWeight: FontWeight.w800,
                          letterSpacing: -1.2,
                        ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Analyze suspicious messages and links for potential scams.',
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                          color: const Color(0xFFB6C2D4),
                          height: 1.5,
                        ),
                  ),
                  const SizedBox(height: 28),
                  AnalysisCard(
                    messageController: _messageController,
                    urlController: _urlController,
                    onScreenshotPressed: () => _showMessage(
                      'Screenshot analysis is not available yet.',
                    ),
                    onScanPressed: _scan,
                  ),
                  if (_isAnalyzing) ...[
                    const SizedBox(height: 24),
                    const Center(
                      child: Column(
                        children: [
                          CircularProgressIndicator(),
                          SizedBox(height: 12),
                          Text('Analyzing with ScamShield...'),
                        ],
                      ),
                    ),
                  ],
                  if (_errorMessage != null) ...[
                    const SizedBox(height: 24),
                    _InfoPanel(
                      title: 'Analysis failed',
                      message: _errorMessage!,
                      color: const Color(0xFFFCA5A5),
                      icon: Icons.error_outline,
                    ),
                  ],
                  if (_result != null) ...[
                    const SizedBox(height: 24),
                    _AnalysisResultCard(result: _result!),
                  ],
                  const SizedBox(height: 32),
                  const SafetyTips(),
                  const SizedBox(height: 32),
                  const RecentChecks(),
                ],
              ),
            ),
          ),
        ),
      );
}

class _AnalysisResultCard extends StatelessWidget {
  const _AnalysisResultCard({required this.result});

  final Map<String, dynamic> result;

  @override
  Widget build(BuildContext context) {
    final prediction =
        (result['prediction'] ?? result['label'] ?? 'UNKNOWN')
            .toString()
            .toUpperCase();

    final riskLevel =
        (result['risk_level'] ?? 'UNKNOWN').toString().toUpperCase();

    final riskScore = (result['risk_score'] as num?)?.toDouble() ?? 0;

    final isScam = prediction == 'SCAM';
    final riskColor = isScam || riskLevel == 'CRITICAL'
        ? const Color(0xFFFCA5A5)
        : riskLevel == 'HIGH'
            ? const Color(0xFFFBBF24)
            : riskLevel == 'MEDIUM'
                ? const Color(0xFFFCD34D)
                : const Color(0xFF6EE7B7);

    final explanation =
        (result['explanation'] ?? 'No explanation provided.').toString();

    final action = (result['recommended_action'] ??
            'Verify the message independently before taking action.')
        .toString();

    final rawFindings = result['findings'];
    final findings = rawFindings is List
        ? rawFindings.map((item) => item.toString()).toSet().toList()
        : <String>[];

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF0D1524),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: riskColor.withValues(alpha: 0.6)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'ANALYSIS RESULT',
            style: TextStyle(
              color: Color(0xFF9AA9BF),
              fontSize: 12,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Icon(
                isScam ? Icons.gpp_bad_outlined : Icons.shield_outlined,
                color: riskColor,
                size: 34,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      prediction == 'SCAM'
                          ? 'Potential Scam Detected'
                          : prediction == 'BENIGN'
                              ? 'No Scam Detected'
                              : prediction,
                      style: TextStyle(
                        color: riskColor,
                        fontSize: 19,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Risk level: $riskLevel',
                      style: TextStyle(color: riskColor),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Risk score',
                style: TextStyle(color: Color(0xFFB6C2D4)),
              ),
              Text(
                '${riskScore.toStringAsFixed(1)} / 100',
                style: TextStyle(
                  color: riskColor,
                  fontWeight: FontWeight.bold,
                  fontSize: 17,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: (riskScore / 100).clamp(0.0, 1.0),
              minHeight: 8,
              backgroundColor: const Color(0xFF273449),
              valueColor: AlwaysStoppedAnimation<Color>(riskColor),
            ),
          ),
          const SizedBox(height: 24),
          _ResultSection(
            title: 'Why this result?',
            content: explanation,
            icon: Icons.info_outline,
          ),
          const SizedBox(height: 20),
          _ResultSection(
            title: 'Recommended action',
            content: action,
            icon: Icons.verified_user_outlined,
          ),
          if (findings.isNotEmpty) ...[
            const SizedBox(height: 20),
            const Text(
              'Suspicious findings',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            for (final finding in findings)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(
                      Icons.warning_amber_rounded,
                      color: Color(0xFFFBBF24),
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Expanded(child: Text(finding)),
                  ],
                ),
              ),
          ],
          const SizedBox(height: 16),
          const Text(
            'AI predictions are estimates, not guarantees. A low risk score does not prove a message is safe.',
            style: TextStyle(
              color: Color(0xFF9AA9BF),
              fontSize: 12,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }
}

class _ResultSection extends StatelessWidget {
  const _ResultSection({
    required this.title,
    required this.content,
    required this.icon,
  });

  final String title;
  final String content;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, color: const Color(0xFF6EE7B7), size: 20),
            const SizedBox(width: 8),
            Text(
              title,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text(
          content,
          style: const TextStyle(
            color: Color(0xFFB6C2D4),
            height: 1.5,
          ),
        ),
      ],
    );
  }
}

class _InfoPanel extends StatelessWidget {
  const _InfoPanel({
    required this.title,
    required this.message,
    required this.color,
    required this.icon,
  });

  final String title;
  final String message;
  final Color color;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF0D1524),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.6)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: TextStyle(color: color)),
                const SizedBox(height: 6),
                Text(message),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
