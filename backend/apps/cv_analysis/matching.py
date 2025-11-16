"""
Job matching algorithm
"""
import logging
from typing import Dict, List
from django.db.models import Q
from .models import CV, JobPosting, JobMatch, CVSkill, JobSkill

logger = logging.getLogger(__name__)


class JobMatchingService:
    """Service for matching CVs to job postings"""
    
    def match_cv_to_job(self, cv: CV, job: JobPosting) -> JobMatch:
        """
        Match a CV to a job posting
        
        Args:
            cv: CV instance
            job: JobPosting instance
        
        Returns:
            JobMatch instance with calculated scores
        """
        # Calculate component scores
        skills_score = self._calculate_skills_match(cv, job)
        experience_score = self._calculate_experience_match(cv, job)
        education_score = self._calculate_education_match(cv, job)
        
        # Calculate overall score (weighted average)
        overall_score = int(
            skills_score['score'] * 0.5 +
            experience_score * 0.3 +
            education_score * 0.2
        )
        
        # Generate match summary
        match_summary = self._generate_match_summary(
            cv, job, overall_score, skills_score
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            cv, job, skills_score
        )
        
        # Create or update match
        match, created = JobMatch.objects.update_or_create(
            cv=cv,
            job=job,
            defaults={
                'overall_score': overall_score,
                'skills_match_score': skills_score['score'],
                'experience_match_score': experience_score,
                'education_match_score': education_score,
                'matched_skills': skills_score['matched'],
                'missing_skills': skills_score['missing'],
                'match_summary': match_summary,
                'recommendations': recommendations,
            }
        )
        
        return match
    
    def _calculate_skills_match(self, cv: CV, job: JobPosting) -> Dict:
        """Calculate skills matching score"""
        # Get CV skills
        cv_skills = set(
            CVSkill.objects.filter(cv=cv).values_list('skill__name', flat=True)
        )
        
        # Get required job skills
        required_skills = JobSkill.objects.filter(job=job, requirement_level='required')
        preferred_skills = JobSkill.objects.filter(job=job, requirement_level='preferred')
        
        required_skill_names = set(s.skill.name for s in required_skills)
        preferred_skill_names = set(s.skill.name for s in preferred_skills)
        
        # Calculate matches
        matched_required = cv_skills & required_skill_names
        matched_preferred = cv_skills & preferred_skill_names
        
        missing_required = required_skill_names - cv_skills
        missing_preferred = preferred_skill_names - cv_skills
        
        # Calculate score
        total_required = len(required_skill_names)
        total_preferred = len(preferred_skill_names)
        
        if total_required == 0 and total_preferred == 0:
            # No specific skills listed, use general match
            score = 70  # Base score
        else:
            # Required skills are worth more
            required_score = (len(matched_required) / total_required * 80) if total_required > 0 else 0
            preferred_score = (len(matched_preferred) / total_preferred * 20) if total_preferred > 0 else 0
            score = int(required_score + preferred_score)
        
        return {
            'score': score,
            'matched': list(matched_required | matched_preferred),
            'missing': list(missing_required | missing_preferred),
            'matched_required': list(matched_required),
            'missing_required': list(missing_required),
        }
    
    def _calculate_experience_match(self, cv: CV, job: JobPosting) -> int:
        """Calculate experience matching score"""
        if not hasattr(cv, 'analysis'):
            return 50  # Default score if no analysis
        
        cv_years = float(cv.analysis.total_years_experience or 0)
        required_years = float(job.years_experience_required or 0)
        
        if required_years == 0:
            return 70  # No specific requirement
        
        if cv_years >= required_years:
            # Has enough experience
            excess = cv_years - required_years
            if excess <= 2:
                return 100  # Perfect match
            elif excess <= 5:
                return 90  # Good match, slightly overqualified
            else:
                return 75  # Overqualified
        else:
            # Under-qualified
            gap = required_years - cv_years
            if gap <= 1:
                return 80  # Close enough
            elif gap <= 2:
                return 60  # Moderate gap
            else:
                return 40  # Significant gap
    
    def _calculate_education_match(self, cv: CV, job: JobPosting) -> int:
        """Calculate education matching score"""
        if not cv.education.exists():
            return 50  # No education info
        
        # Degree hierarchy
        degree_scores = {
            'phd': 100,
            'master': 85,
            'bachelor': 70,
            'associate': 55,
            'high_school': 40,
            'certificate': 45,
            'other': 30,
        }
        
        highest_edu = cv.education.order_by('-degree').first()
        score = degree_scores.get(highest_edu.degree, 50)
        
        return score
    
    def _generate_match_summary(
        self, cv: CV, job: JobPosting, overall_score: int, skills_score: Dict
    ) -> str:
        """Generate match summary text"""
        if overall_score >= 80:
            strength = "Excellent"
        elif overall_score >= 60:
            strength = "Good"
        elif overall_score >= 40:
            strength = "Fair"
        else:
            strength = "Weak"
        
        matched_count = len(skills_score['matched'])
        missing_count = len(skills_score['missing'])
        
        summary = f"{strength} match ({overall_score}%). "
        summary += f"You have {matched_count} matching skills. "
        
        if missing_count > 0:
            summary += f"{missing_count} additional skills would strengthen your application."
        else:
            summary += "You meet all skill requirements!"
        
        return summary
    
    def _generate_recommendations(
        self, cv: CV, job: JobPosting, skills_score: Dict
    ) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Missing required skills
        missing_required = skills_score.get('matched_required', [])
        if missing_required:
            recommendations.append(
                f"Consider gaining experience in: {', '.join(missing_required[:3])}"
            )
        
        # Experience gap
        if hasattr(cv, 'analysis') and job.years_experience_required:
            cv_years = float(cv.analysis.total_years_experience or 0)
            required_years = float(job.years_experience_required)
            
            if cv_years < required_years:
                gap = required_years - cv_years
                recommendations.append(
                    f"Highlight relevant projects to bridge the {gap:.1f} year experience gap"
                )
        
        # General tips
        if skills_score['score'] < 70:
            recommendations.append(
                "Emphasize transferable skills and demonstrate quick learning ability"
            )
        
        if skills_score['score'] >= 80:
            recommendations.append(
                "You're a strong candidate! Tailor your cover letter to highlight matched skills"
            )
        
        return recommendations[:5]  # Limit to top 5
    
    def batch_match(self, cv_id: int, tenant_id: int) -> List[JobMatch]:
        """
        Match a CV to all active jobs for a tenant
        
        Args:
            cv_id: CV ID
            tenant_id: Tenant ID
        
        Returns:
            List of JobMatch instances
        """
        cv = CV.objects.get(id=cv_id, tenant_id=tenant_id)
        jobs = JobPosting.objects.filter(tenant_id=tenant_id, status='active')
        
        matches = []
        for job in jobs:
            try:
                match = self.match_cv_to_job(cv, job)
                matches.append(match)
            except Exception as e:
                logger.error(f"Error matching CV {cv_id} to job {job.id}: {e}")
        
        return matches
