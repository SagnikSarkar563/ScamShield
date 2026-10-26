import 'package:flutter_test/flutter_test.dart';
import 'package:scamshield/app.dart';

void main() {
  testWidgets('shows the ScamShield home screen', (tester) async {
    await tester.pumpWidget(const ScamShieldApp());

    expect(find.text('ScamShield'), findsOneWidget);
    expect(find.text('Analyze suspicious content'), findsOneWidget);
    expect(find.text('Scan for Scam'), findsOneWidget);
  });
}
