import 'package:flutter/material.dart';

class RecentChecks extends StatelessWidget {
  const RecentChecks({super.key});
  @override
  Widget build(BuildContext context) =>
      Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('Recent checks',
            style: Theme.of(context)
                .textTheme
                .titleLarge
                ?.copyWith(fontWeight: FontWeight.w700)),
        const SizedBox(height: 14),
        Card(
            child: Padding(
                padding: const EdgeInsets.all(20),
                child: Row(children: [
                  Container(
                      padding: const EdgeInsets.all(11),
                      decoration: BoxDecoration(
                          color: const Color(0xFF172237),
                          borderRadius: BorderRadius.circular(12)),
                      child: const Icon(Icons.history_toggle_off_rounded)),
                  const SizedBox(width: 14),
                  Expanded(
                      child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                        Text('No scans yet',
                            style: Theme.of(context)
                                .textTheme
                                .titleMedium
                                ?.copyWith(fontWeight: FontWeight.w700)),
                        const SizedBox(height: 4),
                        const Text('Your analyzed messages will appear here.',
                            style: TextStyle(color: Color(0xFF9AA9BF)))
                      ])),
                ]))),
      ]);
}
