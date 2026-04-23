"""
Advanced Features App

Contains three advanced AI features for PhysioAI:

1. Adaptive Difficulty System
   - Tracks performance trends
   - Generates difficulty recommendations
   - Auto-adapts exercise difficulty

2. Injury Risk Detection
   - Monitors joint angles
   - Detects unsafe positions
   - Generates safety alerts

3. Exercise Classification
   - Multi-dimensional classification
   - Intelligent exercise matching
   - Personalized recommendations

Models:
  - DifficultyAdaptation
  - InjuryRiskAlert
  - ExerciseClassification
  - JointSafetyProfile
  - UserDifficultyPreference

Services:
  - AdaptiveDifficultySystem
  - InjuryRiskDetectionSystem
  - ExerciseClassificationSystem

API:
  - DifficultyAdaptationViewSet
  - InjuryRiskAlertViewSet
  - ExerciseClassificationViewSet
  - UserProgressAnalysisViewSet
"""

default_app_config = 'advanced_features.apps.AdvancedFeaturesConfig'
