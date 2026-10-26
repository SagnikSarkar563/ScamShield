import 'package:flutter/material.dart';

class SafetyTips extends StatelessWidget {
  const SafetyTips({super.key});
  static const _tips = [
    (Icons.password_rounded, 'Never share OTPs or passwords.'),
    (
      Icons.account_balance_wallet_outlined,
      'Verify unexpected payment requests.'
    ),
    (Icons.link_off_rounded, "Don't open suspicious links.")
  ];
  @override
  Widget build(BuildContext context) =>
      Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('Stay safe',
            style: Theme.of(context)
                .textTheme
                .titleLarge
                ?.copyWith(fontWeight: FontWeight.w700)),
        const SizedBox(height: 14),
        ..._tips.map((tip) => Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: _SafetyTip(icon: tip.$1, text: tip.$2))),
      ]);
}

class _SafetyTip extends StatelessWidget {
  const _SafetyTip({required this.icon, required this.text});
  final IconData icon;
  final String text;
  @override
  Widget build(BuildContext context) => Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
          color: const Color(0xFF0D1524),
          borderRadius: BorderRadius.circular(14)),
      child: Row(children: [
        Icon(icon, color: Theme.of(context).colorScheme.primary),
        const SizedBox(width: 12),
        Expanded(child: Text(text, style: const TextStyle(height: 1.35)))
      ]));
}
