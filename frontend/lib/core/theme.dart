import 'package:flutter/material.dart';

// ── Reride Brand Colors ──────────────────────────────────────────────────────
class RerideColors {
  RerideColors._();

  static const Color primary = Color(0xFF6C3FE8);       // deep purple
  static const Color primaryLight = Color(0xFF9B6EFF);
  static const Color accent = Color(0xFF3F8CE8);        // snowboard blue
  static const Color accentLight = Color(0xFF6FB3FF);
  static const Color surface = Color(0xFF1A1A2E);       // midnight navy
  static const Color surfaceCard = Color(0xFF16213E);
  static const Color surfaceElevated = Color(0xFF0F3460);
  static const Color background = Color(0xFF0D0D1A);
  static const Color onBackground = Color(0xFFEEEEF5);
  static const Color onSurface = Color(0xFFCCCCDD);
  static const Color divider = Color(0xFF2A2A4A);
  static const Color error = Color(0xFFFF5252);
  static const Color success = Color(0xFF4CAF50);

  // Gradient — used for hero banners, upload button, etc.
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [primary, accent],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}

// ── Theme ────────────────────────────────────────────────────────────────────
ThemeData buildRerideTheme() {
  const colorScheme = ColorScheme.dark(
    primary: RerideColors.primary,
    primaryContainer: RerideColors.surfaceElevated,
    secondary: RerideColors.accent,
    secondaryContainer: Color(0xFF1B3A5C),
    surface: RerideColors.surface,
    error: RerideColors.error,
    onPrimary: Colors.white,
    onSecondary: Colors.white,
    onSurface: RerideColors.onSurface,
    onError: Colors.white,
    outline: RerideColors.divider,
  );

  return ThemeData(
    useMaterial3: true,
    colorScheme: colorScheme,
    scaffoldBackgroundColor: RerideColors.background,

    // AppBar
    appBarTheme: const AppBarTheme(
      backgroundColor: RerideColors.surface,
      foregroundColor: RerideColors.onBackground,
      elevation: 0,
      centerTitle: true,
      titleTextStyle: TextStyle(
        fontSize: 20,
        fontWeight: FontWeight.w700,
        color: RerideColors.onBackground,
        letterSpacing: 1.5,
      ),
    ),

    // Cards
    cardTheme: CardThemeData(
      color: RerideColors.surfaceCard,
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
    ),

    // Elevated Button
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: RerideColors.primary,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
      ),
    ),

    // Outlined Button
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: RerideColors.primaryLight,
        side: const BorderSide(color: RerideColors.primary, width: 1.5),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    ),

    // Text Button
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: RerideColors.accentLight,
        textStyle: const TextStyle(fontWeight: FontWeight.w600),
      ),
    ),

    // Floating Action Button
    floatingActionButtonTheme: const FloatingActionButtonThemeData(
      backgroundColor: RerideColors.primary,
      foregroundColor: Colors.white,
      elevation: 6,
    ),

    // Input / TextField
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: RerideColors.surfaceCard,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: RerideColors.divider),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: RerideColors.divider),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: RerideColors.primary, width: 2),
      ),
      labelStyle: const TextStyle(color: RerideColors.onSurface),
    ),

    // BottomNavigationBar
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: RerideColors.surface,
      selectedItemColor: RerideColors.primaryLight,
      unselectedItemColor: Colors.white38,
      type: BottomNavigationBarType.fixed,
      elevation: 8,
    ),

    // Divider
    dividerTheme: const DividerThemeData(
      color: RerideColors.divider,
      thickness: 1,
    ),

    // Text
    textTheme: const TextTheme(
      displayLarge: TextStyle(color: RerideColors.onBackground, fontWeight: FontWeight.w800),
      displayMedium: TextStyle(color: RerideColors.onBackground, fontWeight: FontWeight.w700),
      headlineLarge: TextStyle(color: RerideColors.onBackground, fontWeight: FontWeight.w700),
      headlineMedium: TextStyle(color: RerideColors.onBackground, fontWeight: FontWeight.w600),
      titleLarge: TextStyle(color: RerideColors.onBackground, fontWeight: FontWeight.w600),
      titleMedium: TextStyle(color: RerideColors.onSurface),
      bodyLarge: TextStyle(color: RerideColors.onSurface),
      bodyMedium: TextStyle(color: RerideColors.onSurface),
      labelLarge: TextStyle(color: RerideColors.onBackground, fontWeight: FontWeight.w600),
    ),
  );
}
