
import 'package:flutter/material.dart';

class ScamShieldHeader extends StatelessWidget {
  const ScamShieldHeader({super.key});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 46,
          height: 46,
          decoration: BoxDecoration(
            color: const Color(0xFF163A36),
            borderRadius: BorderRadius.circular(14),
          ),
          child: const Icon(
            Icons.shield_outlined,
            color: Color(0xFF6EE7B7),
            size: 28,
          ),
        ),
        const SizedBox(width: 12),
        const Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'ScamShield',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.w800,
                ),
              ),
              SizedBox(height: 2),
              Text(
                'Stay alert. Stay protected.',
                style: TextStyle(
                  color: Color(0xFF9AA9BF),
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
