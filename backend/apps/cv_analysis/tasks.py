"""
Celery tasks for CV analysis
"""
from celery import shared_task
import logging
from .services import CVProcessingService
from .models import CV

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_cv_task(self, cv_id: int):
    """
    Process a CV asynchronously
    
    Args:
        cv_id: CV ID to process
    
    Returns:
        dict: Processing result
    """
    try:
        analysis = CVProcessingService.process_cv(cv_id)
        return {
            'success': True,
            'cv_id': cv_id,
            'analysis_id': analysis.id,
            'overall_score': analysis.overall_score
        }
    except CV.DoesNotExist:
        logger.error(f"CV {cv_id} not found")
        return {'success': False, 'error': 'CV not found'}
    except Exception as e:
        logger.error(f"Error processing CV {cv_id}: {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task
def batch_process_cvs(cv_ids: list):
    """
    Process multiple CVs in batch
    
    Args:
        cv_ids: List of CV IDs
    
    Returns:
        dict: Batch processing results
    """
    results = []
    for cv_id in cv_ids:
        try:
            process_cv_task.delay(cv_id)
            results.append({'cv_id': cv_id, 'status': 'queued'})
        except Exception as e:
            logger.error(f"Error queuing CV {cv_id}: {e}")
            results.append({'cv_id': cv_id, 'status': 'failed', 'error': str(e)})
    
    return {
        'total': len(cv_ids),
        'queued': len([r for r in results if r['status'] == 'queued']),
        'failed': len([r for r in results if r['status'] == 'failed']),
        'results': results
    }


@shared_task
def cleanup_old_cvs():
    """
    Clean up old processed CVs (run periodically)
    Deletes CVs older than 90 days
    """
    from django.utils import timezone
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=90)
    old_cvs = CV.objects.filter(created_at__lt=cutoff_date)
    count = old_cvs.count()
    
    # Delete files
    for cv in old_cvs:
        try:
            cv.file.delete()
        except:
            pass
    
    # Delete records
    old_cvs.delete()
    
    logger.info(f"Cleaned up {count} old CVs")
    return {'cleaned': count}


@shared_task
def generate_skill_insights():
    """
    Generate insights about skill trends across all CVs
    Run periodically to update skill statistics
    """
    from django.db.models import Count, Avg
    from .models import CVSkill, Skill
    
    # Most common skills
    common_skills = Skill.objects.annotate(
        cv_count=Count('cv_skills')
    ).filter(cv_count__gt=0).order_by('-cv_count')[:20]
    
    # Average confidence by category
    category_confidence = CVSkill.objects.values('skill__category').annotate(
        avg_confidence=Avg('confidence'),
        count=Count('id')
    )
    
    insights = {
        'common_skills': [
            {'skill': s.name, 'count': s.cv_count}
            for s in common_skills
        ],
        'category_confidence': list(category_confidence)
    }
    
    logger.info(f"Generated skill insights: {len(common_skills)} common skills")
    return insights
