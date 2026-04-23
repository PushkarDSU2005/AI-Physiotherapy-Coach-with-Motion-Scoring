"""
Signals for therapy_plans app.
Used for automatic updates and notifications when therapy plans are created or modified.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
import logging

from therapy_plans.models import TherapyPlan, WeeklyExercise

logger = logging.getLogger(__name__)


@receiver(post_save, sender=TherapyPlan)
def invalidate_plan_cache(sender, instance, created, **kwargs):
    """
    Invalidate cache when a therapy plan is created or updated.
    
    This ensures that cached API responses are updated when plans change.
    """
    try:
        # Clear cache for this user's plans
        cache_key = f'user_{instance.user.id}_therapy_plans'
        cache.delete(cache_key)
        
        # Clear specific plan cache
        cache_key = f'therapy_plan_{instance.id}'
        cache.delete(cache_key)
        
        if created:
            logger.info(f"New therapy plan created: {instance.id} for user {instance.user.username}")
        else:
            logger.info(f"Therapy plan updated: {instance.id}")
            
    except Exception as e:
        logger.warning(f"Error invalidating cache for therapy plan: {str(e)}")


@receiver(post_save, sender=WeeklyExercise)
def invalidate_exercise_cache(sender, instance, created, **kwargs):
    """
    Invalidate cache when a weekly exercise is created or updated.
    
    This ensures that weekly schedules are updated in the cache.
    """
    try:
        # Clear cache for the therapy plan's schedule
        cache_key = f'therapy_plan_{instance.therapy_plan.id}_schedule'
        cache.delete(cache_key)
        
        if created:
            logger.debug(f"New weekly exercise created: Week {instance.week_number} {instance.day_of_week}")
        else:
            logger.debug(f"Weekly exercise updated: Week {instance.week_number} {instance.day_of_week}")
            
    except Exception as e:
        logger.warning(f"Error invalidating cache for weekly exercise: {str(e)}")


@receiver(post_delete, sender=TherapyPlan)
def log_plan_deletion(sender, instance, **kwargs):
    """
    Log when a therapy plan is deleted.
    """
    logger.info(f"Therapy plan deleted: {instance.id} for user {instance.user.username}")


@receiver(post_delete, sender=WeeklyExercise)
def log_exercise_deletion(sender, instance, **kwargs):
    """
    Log when a weekly exercise is deleted.
    """
    logger.debug(f"Weekly exercise deleted: Week {instance.week_number} {instance.day_of_week}")
