"""
Models for CV Analysis modules supporting 3 different analysis types:
1. ATS Score Checker (Free with limits)
2. CV-Job Matcher (Free with limits)
3. Advanced CV Analyzer (Premium)
"""
import uuid
from django.db import models
from django.conf import settings
from apps.core.models import TimestampedModel, Tenant

User = settings.AUTH_USER_MODEL


class CVAnalysisUsageTracker(TimestampedModel):
    """
    Tracks free tier usage for ATS checker and CV-Job matcher.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='cv_usage_trackers')
    module_type = models.CharField(
        max_length=50,
        choices=[
            ('ats_detailed', 'ATS Detailed Reports'),
            ('cv_matcher', 'CV-Job Matches'),
        ]
    )
    
    # Usage tracking
    free_limit = models.IntegerField(default=3)  # Free uses allowed
    used_count = models.IntegerField(default=0)  # Times used
    
    class Meta:
        db_table = 'cv_analysis_usage_trackers'
        unique_together = ['tenant', 'module_type']
    
    def __str__(self):
        return f"{self.tenant.name} - {self.module_type}: {self.used_count}/{self.free_limit}"
    
    @property
    def can_use_free(self):
        """Check if tenant can still use free tier."""
        return self.used_count < self.free_limit
    
    @property
    def remaining_uses(self):
        """Get remaining free uses."""
        return max(0, self.free_limit - self.used_count)


class CV(TimestampedModel):
    """Stores uploaded CVs"""
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('analyzed', 'Analyzed'),
        ('failed', 'Failed'),
    ]
    
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='cvs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cvs')
    
    file = models.FileField(upload_to='cvs/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10)  # pdf, docx, txt
    file_size = models.IntegerField()  # bytes
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    
    # Extracted text
    raw_text = models.TextField(blank=True)
    
    # Processing metadata
    processed_at = models.DateTimeField(null=True, blank=True)
    processing_error = models.TextField(blank=True)
    
    class Meta:
        db_table = 'cv_analysis_cvs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
        verbose_name = 'CV'
        verbose_name_plural = 'CVs'
    
    def __str__(self):
        return f"{self.filename} - {self.user.email} ({self.status})"


class CVAnalysis(TimestampedModel):
    """Stores analysis results for a CV"""
    cv = models.OneToOneField(CV, on_delete=models.CASCADE, related_name='analysis')
    
    # Personal Information
    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=255, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    
    # Summary
    professional_summary = models.TextField(blank=True)
    
    # Experience
    total_years_experience = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    
    # Education
    highest_degree = models.CharField(max_length=100, blank=True)
    
    # Scores (0-100)
    overall_score = models.IntegerField(default=0)
    experience_score = models.IntegerField(default=0)
    education_score = models.IntegerField(default=0)
    skills_score = models.IntegerField(default=0)
    formatting_score = models.IntegerField(default=0)
    
    # AI-generated insights
    strengths = models.JSONField(default=list, blank=True)  # List of strings
    weaknesses = models.JSONField(default=list, blank=True)  # List of strings
    suggestions = models.JSONField(default=list, blank=True)  # List of strings
    
    # Metadata
    analysis_version = models.CharField(max_length=10, default='1.0')
    
    class Meta:
        db_table = 'cv_analysis_analyses'
        verbose_name = 'CV Analysis'
        verbose_name_plural = 'CV Analyses'
    
    def __str__(self):
        return f"Analysis for {self.cv.filename}"


class Skill(TimestampedModel):
    """Skill taxonomy"""
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50)  # Technical, Soft, Language, Tool, etc.
    synonyms = models.JSONField(default=list, blank=True)  # Alternative names
    
    # For matching
    importance_weight = models.FloatField(default=1.0)
    
    class Meta:
        db_table = 'cv_analysis_skills'
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.category})"


class CVSkill(TimestampedModel):
    """Skills extracted from a CV"""
    PROFICIENCY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='cv_skills')
    
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, blank=True)
    years_experience = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    
    # Confidence score from NLP extraction (0-100)
    confidence = models.IntegerField(default=0)
    
    # Context where skill was mentioned
    context = models.TextField(blank=True)
    
    class Meta:
        db_table = 'cv_analysis_cv_skills'
        unique_together = ['cv', 'skill']
        ordering = ['-confidence', 'skill__name']
    
    def __str__(self):
        return f"{self.skill.name} in {self.cv.filename}"


class Experience(TimestampedModel):
    """Work experience extracted from CV"""
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='experiences')
    
    company = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    
    description = models.TextField(blank=True)
    achievements = models.JSONField(default=list, blank=True)  # List of achievement strings
    
    # Calculated
    duration_months = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'cv_analysis_experiences'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.position} at {self.company}"
    
    def save(self, *args, **kwargs):
        # Calculate duration
        if self.start_date:
            from django.utils import timezone
            end = self.end_date or timezone.now().date()
            self.duration_months = (end.year - self.start_date.year) * 12 + (end.month - self.start_date.month)
        super().save(*args, **kwargs)


class Education(TimestampedModel):
    """Education history extracted from CV"""
    DEGREE_CHOICES = [
        ('high_school', 'High School'),
        ('associate', 'Associate Degree'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('phd', 'PhD'),
        ('certificate', 'Certificate'),
        ('other', 'Other'),
    ]
    
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='education')
    
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=50, choices=DEGREE_CHOICES)
    field_of_study = models.CharField(max_length=255, blank=True)
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    
    grade = models.CharField(max_length=50, blank=True)  # GPA, honors, etc.
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'cv_analysis_education'
        ordering = ['-end_date']
    
    def __str__(self):
        return f"{self.degree} at {self.institution}"


class JobPosting(TimestampedModel):
    """Job postings for matching"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('draft', 'Draft'),
    ]
    
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='job_postings')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_postings')
    
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    description = models.TextField()
    requirements = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # External job posting
    external_url = models.URLField(blank=True)
    source = models.CharField(max_length=100, blank=True)  # LinkedIn, Indeed, etc.
    
    # For matching
    years_experience_required = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    
    class Meta:
        db_table = 'cv_analysis_job_postings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.title} at {self.company}"


class JobSkill(TimestampedModel):
    """Skills required for a job"""
    REQUIREMENT_LEVEL_CHOICES = [
        ('required', 'Required'),
        ('preferred', 'Preferred'),
        ('nice_to_have', 'Nice to Have'),
    ]
    
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='required_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='job_skills')
    
    requirement_level = models.CharField(max_length=20, choices=REQUIREMENT_LEVEL_CHOICES, default='required')
    years_required = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    
    class Meta:
        db_table = 'cv_analysis_job_skills'
        unique_together = ['job', 'skill']
    
    def __str__(self):
        return f"{self.skill.name} for {self.job.title}"


class JobMatch(TimestampedModel):
    """CV to Job matching results"""
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='job_matches')
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='cv_matches')
    
    # Match score (0-100)
    overall_score = models.IntegerField()
    skills_match_score = models.IntegerField()
    experience_match_score = models.IntegerField()
    education_match_score = models.IntegerField()
    
    # Detailed matching
    matched_skills = models.JSONField(default=list, blank=True)  # List of skill names
    missing_skills = models.JSONField(default=list, blank=True)  # List of skill names
    
    # AI-generated analysis
    match_summary = models.TextField(blank=True)
    recommendations = models.JSONField(default=list, blank=True)  # List of recommendation strings
    
    # User interaction
    is_bookmarked = models.BooleanField(default=False)
    applied_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'cv_analysis_job_matches'
        unique_together = ['cv', 'job']
        ordering = ['-overall_score', '-created_at']
        indexes = [
            models.Index(fields=['cv', '-overall_score']),
            models.Index(fields=['job', '-overall_score']),
        ]
    
    def __str__(self):
        return f"{self.cv.filename} → {self.job.title} ({self.overall_score}%)"


class ATSAnalysis(TimestampedModel):
    """
    ATS Score Checker Module - Free with limited detailed reports
    Always provides basic score + keywords, detailed report limited to 3 free uses
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='ats_analyses')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ats_analyses')
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='ats_analyses')
    
    # ATS Score (Always available - FREE)
    ats_score = models.IntegerField()  # 0-100
    
    # Keywords Analysis (Always available - FREE)
    keyword_matches = models.JSONField(default=list, blank=True)  # Keywords found in CV
    missing_keywords = models.JSONField(default=list, blank=True)  # Keywords to add
    quick_suggestions = models.JSONField(default=list, blank=True)  # 3-5 quick tips
    
    # Detailed Report (Limited to 3 free uses, then paid)
    has_detailed_report = models.BooleanField(default=False)
    detailed_report = models.TextField(blank=True)  # Comprehensive AI analysis
    
    # Status
    is_free_detailed_report = models.BooleanField(default=False)  # Track if this used a free report
    
    class Meta:
        db_table = 'ats_analyses'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"ATS Analysis {self.ats_score}% - {self.user.email}"


class CVJobMatch(TimestampedModel):
    """
    CV-Job Matcher Module - Free with 3 matches limit
    Match CV with job description, limited to 3 free uses
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='cv_job_matches')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cv_job_matches')
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='cv_job_matches')
    
    # Job description input
    job_title = models.CharField(max_length=255)
    job_description = models.TextField()
    
    # Matching results
    match_score = models.IntegerField()  # 0-100
    matched_skills = models.JSONField(default=list, blank=True)
    missing_skills = models.JSONField(default=list, blank=True)
    matching_report = models.TextField()  # AI-generated matching analysis
    
    # Recommendations
    recommendations = models.JSONField(default=list, blank=True)
    
    # Status
    is_free_match = models.BooleanField(default=False)  # Track if this used a free match
    
    class Meta:
        db_table = 'cv_job_matches'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"CV-Job Match {self.match_score}% - {self.job_title}"


class AdvancedCVAnalysis(TimestampedModel):
    """
    Advanced CV Analyzer Module - Premium only
    Full AI-powered CV analysis with comprehensive insights and chatbot
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='advanced_analyses')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='advanced_analyses')
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='advanced_analyses')
    
    # Comprehensive AI Analysis
    full_analysis = models.TextField(default='Analysis in progress...', blank=True)  # Executive summary
    strengths = models.JSONField(default=list, blank=True)  # List of key strengths
    weaknesses = models.JSONField(default=list, blank=True)  # Areas for improvement
    improvement_suggestions = models.JSONField(default=list, blank=True)  # Action items
    career_recommendations = models.JSONField(default=list, blank=True)  # Career insights
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='completed'
    )
    
    class Meta:
        db_table = 'advanced_cv_analyses'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Advanced Analysis - {self.user.email}"


class ChatMessage(TimestampedModel):
    """
    Chat messages for Advanced CV Analyzer chatbot feature
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    advanced_analysis = models.ForeignKey(
        AdvancedCVAnalysis, 
        on_delete=models.CASCADE, 
        related_name='chat_messages'
    )
    
    role = models.CharField(
        max_length=20,
        choices=[
            ('user', 'User'),
            ('assistant', 'Assistant'),
        ]
    )
    content = models.TextField()
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
