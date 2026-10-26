import 'package:flutter/material.dart';

import 'screens/history_screen.dart';
import 'screens/home_screen.dart';
import 'screens/settings_screen.dart';
import 'theme/app_theme.dart';

class ScamShieldApp extends StatefulWidget {
  const ScamShieldApp({super.key});

  @override
  State<ScamShieldApp> createState() => _ScamShieldAppState();
}

class _ScamShieldAppState extends State<ScamShieldApp> {
  var _selectedIndex = 0;
  static const _pages = <Widget>[
    HomeScreen(),
    HistoryScreen(),
    SettingsScreen()
  ];

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'ScamShield',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.darkTheme,
        home: Scaffold(
          body: SafeArea(child: _pages[_selectedIndex]),
          bottomNavigationBar: NavigationBar(
            selectedIndex: _selectedIndex,
            onDestinationSelected: (index) =>
                setState(() => _selectedIndex = index),
            destinations: const [
              NavigationDestination(
                  icon: Icon(Icons.home_outlined),
                  selectedIcon: Icon(Icons.home_rounded),
                  label: 'Home'),
              NavigationDestination(
                  icon: Icon(Icons.history_outlined),
                  selectedIcon: Icon(Icons.history_rounded),
                  label: 'History'),
              NavigationDestination(
                  icon: Icon(Icons.settings_outlined),
                  selectedIcon: Icon(Icons.settings_rounded),
                  label: 'Settings'),
            ],
          ),
        ),
      );
}
