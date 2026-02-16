import 'package:flutter/material.dart';

/// Reride 앱의 스노보드 영감 색상 팔레트
class AppColors {
  AppColors._();

  // Background / Surface
  static const Color background = Color(0xFF0A0E1A);
  static const Color surface = Color(0xFF131929);
  static const Color surfaceVariant = Color(0xFF1E2A3D);
  static const Color cardBackground = Color(0xFF1A2236);

  // Primary - Ice Blue (눈과 얼음)
  static const Color primary = Color(0xFF00B4D8);
  static const Color primaryLight = Color(0xFF48CAE4);
  static const Color primaryDark = Color(0xFF0077A8);

  // Secondary - Mountain Snow (설원)
  static const Color secondary = Color(0xFF90E0EF);
  static const Color secondaryLight = Color(0xFFCAF0F8);

  // Accent - Neon Powder (파우더 라이딩)
  static const Color accent = Color(0xFF00F5FF);
  static const Color accentOrange = Color(0xFFFF6B35); // 석양 / 경고

  // Status
  static const Color success = Color(0xFF4ADE80);
  static const Color warning = Color(0xFFFFB347);
  static const Color error = Color(0xFFFF5252);
  static const Color info = Color(0xFF48CAE4);

  // Score colors
  static const Color scoreExcellent = Color(0xFF4ADE80); // 90+
  static const Color scoreGood = Color(0xFF00B4D8);      // 70-89
  static const Color scoreAverage = Color(0xFFFFB347);   // 50-69
  static const Color scorePoor = Color(0xFFFF5252);      // <50

  // Text
  static const Color textPrimary = Color(0xFFF0F4FF);
  static const Color textSecondary = Color(0xFF8899B8);
  static const Color textDisabled = Color(0xFF3D4F6A);

  // Gradient
  static const LinearGradient primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primary, primaryDark],
  );

  static const LinearGradient backgroundGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [Color(0xFF0A0E1A), Color(0xFF131929)],
  );

  static const LinearGradient cardGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFF1A2236), Color(0xFF131929)],
  );
}
