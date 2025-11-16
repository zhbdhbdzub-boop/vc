from django.db import models
from django.conf import settings
from apps.core.models import TimestampedModel


class InterviewTemplate(TimestampedModel):
    """Predefined interview templates"""
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    INTERVIEW_TYPE_CHOICES = [
        ('technical', 'Technical'),
        ('behavioral', 'Behavioral'),
        ('case_study', 'Case Study'),
        ('system_design', 'System Design'),
        ('cultural_fit', 'Cultural Fit'),
    ]
    
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='interview_templates', null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    interview_type = models.CharField(max_length=30, choices=INTERVIEW_TYPE_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    
    # Target audience
    job_role = models.CharField(max_length=255, blank=True)  # e.g., "Software Engineer", "Product Manager"
    experience_level = models.CharField(max_length=50, blank=True)  # e.g., "Junior", "Senior"
    
    # Configuration
    duration_minutes = models.IntegerField(default=30)
    question_count = models.IntegerField(default=10)
    
    # Template or public
    is_public = models.BooleanField(default=False)  # Public templates available to all
    is_active = models.BooleanField(default=True)
    
    # Usage stats
    usage_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'interviews_templates'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['interview_type', 'difficulty']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.interview_type} - {self.difficulty})"


class InterviewSession(TimestampedModel):
    """Individual interview session - Real-time AI Interview Simulation"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    MODE_CHOICES = [
        ('practice', 'Practice Mode'),
        ('simulation', 'Real Simulation'),
    ]
    
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='interview_sessions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interview_sessions')
    template = models.ForeignKey(InterviewTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    
    title = models.CharField(max_length=255)
    job_role = models.CharField(max_length=255, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='practice')
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(default=0)
    
    # Overall scores
    overall_score = models.IntegerField(default=0)  # 0-100
    technical_score = models.IntegerField(default=0)
    communication_score = models.IntegerField(default=0)
    confidence_score = models.IntegerField(default=0)
    problem_solving_score = models.IntegerField(default=0)
    
    # AI-generated feedback
    overall_feedback = models.TextField(blank=True)
    strengths = models.JSONField(default=list, blank=True)
    areas_for_improvement = models.JSONField(default=list, blank=True)
    recommendations = models.JSONField(default=list, blank=True)
    
    # Real-time features
    interviewer_avatar_url = models.URLField(blank=True)  # AI interviewer avatar
    recording_url = models.URLField(blank=True)  # Session recording
    transcript = models.TextField(blank=True)  # Full conversation transcript
    
    # Analytics
    response_times = models.JSONField(default=list, blank=True)  # Time taken for each answer
    filler_words_count = models.IntegerField(default=0)
    speaking_pace = models.CharField(max_length=20, blank=True)  # slow/moderate/fast
    
    class Meta:
        db_table = 'interviews_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'user', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.email} ({self.status})"


class Question(TimestampedModel):
    """Interview questions"""
    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('coding', 'Coding'),
        ('open_ended', 'Open Ended'),
        ('behavioral', 'Behavioral'),
        ('system_design', 'System Design'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    template = models.ForeignKey(InterviewTemplate, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    
    question_type = models.CharField(max_length=30, choices=QUESTION_TYPE_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    
    question_text = models.TextField()
    context = models.TextField(blank=True)  # Additional context or setup
    
    # For multiple choice
    options = models.JSONField(default=list, blank=True)  # List of option strings
    correct_answer = models.TextField(blank=True)
    
    # For coding questions
    starter_code = models.TextField(blank=True)
    test_cases = models.JSONField(default=list, blank=True)
    
    # Expected answer/rubric
    ideal_answer = models.TextField(blank=True)
    evaluation_criteria = models.JSONField(default=list, blank=True)
    
    # Metadata
    tags = models.JSONField(default=list, blank=True)  # e.g., ["python", "algorithms", "arrays"]
    time_limit_seconds = models.IntegerField(default=300)  # 5 minutes default
    
    class Meta:
        db_table = 'interviews_questions'
        ordering = ['difficulty', 'question_type']
        indexes = [
            models.Index(fields=['template']),
            models.Index(fields=['question_type', 'difficulty']),
        ]
    
    def __str__(self):
        return f"{self.question_type} - {self.question_text[:50]}..."


class SessionQuestion(TimestampedModel):
    """Questions asked in a specific session"""
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='session_questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='session_questions')
    
    order = models.IntegerField(default=0)
    
    # User's answer
    user_answer = models.TextField(blank=True)
    
    # For coding questions
    code_submission = models.TextField(blank=True)
    execution_result = models.JSONField(default=dict, blank=True)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_taken_seconds = models.IntegerField(default=0)
    
    # Evaluation
    is_correct = models.BooleanField(default=False)
    score = models.IntegerField(default=0)  # 0-100
    ai_evaluation = models.TextField(blank=True)
    
    # Sentiment analysis (for open-ended questions)
    sentiment = models.CharField(max_length=20, blank=True)  # positive, neutral, negative
    confidence_level = models.IntegerField(default=0)  # 0-100
    
    class Meta:
        db_table = 'interviews_session_questions'
        ordering = ['session', 'order']
        unique_together = ['session', 'question']
    
    def __str__(self):
        return f"Q{self.order} in {self.session.title}"


class InterviewFeedback(TimestampedModel):
    """Detailed feedback for interview sessions"""
    session = models.OneToOneField(InterviewSession, on_delete=models.CASCADE, related_name='detailed_feedback')
    
    # Performance breakdown
    technical_analysis = models.TextField(blank=True)
    communication_analysis = models.TextField(blank=True)
    problem_solving_analysis = models.TextField(blank=True)
    
    # Specific strengths and weaknesses
    strong_areas = models.JSONField(default=list, blank=True)
    weak_areas = models.JSONField(default=list, blank=True)
    
    # Recommendations
    study_topics = models.JSONField(default=list, blank=True)  # Topics to study
    resource_links = models.JSONField(default=list, blank=True)  # Helpful resources
    
    # Comparison to other candidates
    percentile_rank = models.IntegerField(null=True, blank=True)  # 0-100
    
    # Next steps
    recommended_difficulty = models.CharField(max_length=20, blank=True)
    ready_for_real_interview = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'interviews_feedback'
        verbose_name = 'Interview Feedback'
        verbose_name_plural = 'Interview Feedback'
    
    def __str__(self):
        return f"Feedback for {self.session.title}"


class PracticeArea(TimestampedModel):
    """Track user's practice progress in different areas"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='practice_areas')
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='practice_areas')
    
    area_name = models.CharField(max_length=100)  # e.g., "Data Structures", "System Design"
    category = models.CharField(max_length=50)  # e.g., "Technical", "Behavioral"
    
    # Progress
    questions_attempted = models.IntegerField(default=0)
    questions_correct = models.IntegerField(default=0)
    total_practice_time_minutes = models.IntegerField(default=0)
    
    # Performance
    current_score = models.IntegerField(default=0)  # 0-100
    best_score = models.IntegerField(default=0)
    last_practiced_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'interviews_practice_areas'
        unique_together = ['user', 'tenant', 'area_name']
        ordering = ['-last_practiced_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.area_name}"


class ConversationMessage(TimestampedModel):
    """Real-time conversation messages during interview"""
    MESSAGE_ROLE_CHOICES = [
        ('interviewer', 'AI Interviewer'),
        ('candidate', 'User/Candidate'),
        ('system', 'System Message'),
    ]
    
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='conversation_messages')
    role = models.CharField(max_length=20, choices=MESSAGE_ROLE_CHOICES)
    content = models.TextField()
    
    # Audio/video metadata
    audio_url = models.URLField(blank=True)
    duration_seconds = models.FloatField(default=0)
    
    # AI analysis (for candidate responses)
    sentiment = models.CharField(max_length=20, blank=True)
    confidence_score = models.IntegerField(default=0)  # 0-100
    keywords_detected = models.JSONField(default=list, blank=True)
    
    # Timestamp within session
    timestamp_seconds = models.FloatField(default=0)  # Seconds from session start
    
    class Meta:
        db_table = 'interviews_conversation_messages'
        ordering = ['session', 'timestamp_seconds']
        indexes = [
            models.Index(fields=['session', 'timestamp_seconds']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."

