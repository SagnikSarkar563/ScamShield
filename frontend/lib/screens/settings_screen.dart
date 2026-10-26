
import 'package:flutter/material.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(24),
      children: const [
        SizedBox(height: 20),
        Text(
          'Settings',
          style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
        ),
        SizedBox(height: 12),
        Text(
          'ScamShield recovery build',
          style: TextStyle(color: Color(0xFF9AA9BF)),
        ),
        SizedBox(height: 24),
        ListTile(
          leading: Icon(Icons.security_outlined),
          title: Text('Safety'),
          subtitle: Text(
            'Never share OTPs, passwords, or UPI PINs with unverified contacts.',
          ),
        ),
        ListTile(
          leading: Icon(Icons.info_outline),
          title: Text('About ScamShield'),
          subtitle: Text(
            'AI-assisted scam detection. Results are estimates, not guarantees.',
          ),
        ),
      ],
    );
  }
}
