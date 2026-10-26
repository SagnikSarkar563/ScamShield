import 'package:flutter/material.dart';

class AnalysisCard extends StatelessWidget {
  const AnalysisCard(
      {required this.messageController,
      required this.urlController,
      required this.onScreenshotPressed,
      required this.onScanPressed,
      super.key});
  final TextEditingController messageController;
  final TextEditingController urlController;
  final VoidCallback onScreenshotPressed;
  final VoidCallback onScanPressed;
  @override
  Widget build(BuildContext context) => Card(
      child: Padding(
          padding: const EdgeInsets.all(20),
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(children: [
              Icon(Icons.radar_rounded,
                  color: Theme.of(context).colorScheme.primary),
              const SizedBox(width: 10),
              Expanded(
                child: Text('Analyze suspicious content',
                    style: Theme.of(context)
                        .textTheme
                        .titleLarge
                        ?.copyWith(fontWeight: FontWeight.w700)),
              )
            ]),
            const SizedBox(height: 20),
            const _FieldLabel(
                icon: Icons.chat_bubble_outline_rounded, label: 'Message'),
            const SizedBox(height: 8),
            TextField(
                controller: messageController,
                keyboardType: TextInputType.multiline,
                maxLines: 4,
                minLines: 3,
                textCapitalization: TextCapitalization.sentences,
                decoration: const InputDecoration(
                    hintText: 'Paste a suspicious message here...')),
            const SizedBox(height: 18),
            const _FieldLabel(icon: Icons.image_outlined, label: 'Screenshot'),
            const SizedBox(height: 8),
            OutlinedButton.icon(
                onPressed: onScreenshotPressed,
                icon: const Icon(Icons.upload_file_rounded),
                label: const Text('Upload Screenshot'),
                style: OutlinedButton.styleFrom(
                    minimumSize: const Size.fromHeight(52),
                    alignment: Alignment.centerLeft)),
            const SizedBox(height: 18),
            const _FieldLabel(icon: Icons.link_rounded, label: 'URL'),
            const SizedBox(height: 8),
            TextField(
                controller: urlController,
                keyboardType: TextInputType.url,
                autocorrect: false,
                enableSuggestions: false,
                decoration: const InputDecoration(
                    hintText: 'Paste a suspicious URL...')),
            const SizedBox(height: 22),
            FilledButton.icon(
                onPressed: onScanPressed,
                icon: const Icon(Icons.shield_outlined),
                label: const Text('Scan for Scam'),
                style: FilledButton.styleFrom(
                    minimumSize: const Size.fromHeight(54),
                    textStyle: const TextStyle(
                        fontSize: 16, fontWeight: FontWeight.w700))),
          ])));
}

class _FieldLabel extends StatelessWidget {
  const _FieldLabel({required this.icon, required this.label});
  final IconData icon;
  final String label;
  @override
  Widget build(BuildContext context) => Row(children: [
        Icon(icon, size: 18, color: const Color(0xFFB6C2D4)),
        const SizedBox(width: 8),
        Text(label, style: const TextStyle(fontWeight: FontWeight.w700))
      ]);
}
