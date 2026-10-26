import 'package:flutter/material.dart';

abstract final class AppTheme {
  static final darkTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    colorScheme: ColorScheme.fromSeed(
        seedColor: const Color(0xFF34D399),
        brightness: Brightness.dark,
        surface: const Color(0xFF111827)),
    scaffoldBackgroundColor: const Color(0xFF080D18),
    cardTheme: CardThemeData(
        color: const Color(0xFF111827),
        elevation: 0,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20))),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: const Color(0xFF0B1220),
      hintStyle: const TextStyle(color: Color(0xFF94A3B8)),
      contentPadding: const EdgeInsets.all(16),
      border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: Color(0xFF273449))),
      enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: Color(0xFF273449))),
      focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: Color(0xFF34D399), width: 1.5)),
    ),
    navigationBarTheme: NavigationBarThemeData(
        backgroundColor: const Color(0xFF0D1524),
        indicatorColor: const Color(0xFF174B45)),
  );
}
