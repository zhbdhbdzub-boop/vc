# code_assessment app
from django.db import models
from apps.core.models import Tenant
from django.contrib.auth import get_user_model

User = get_user_model()


class CodingProblem(models.Model):
    """Coding challenge problem"""
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    CATEGORY_CHOICES = [
        ('arrays', 'Arrays'),
        ('strings', 'Strings'),
        ('linked_lists', 'Linked Lists'),
        ('trees', 'Trees'),
        ('graphs', 'Graphs'),
        ('dynamic_programming', 'Dynamic Programming'),
        ('sorting', 'Sorting'),
        ('searching', 'Searching'),
        ('recursion', 'Recursion'),
        ('greedy', 'Greedy'),
        ('backtracking', 'Backtracking'),
        ('bit_manipulation', 'Bit Manipulation'),
        ('math', 'Math'),
        ('database', 'Database'),
        ('other', 'Other'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='coding_problems', null=True, blank=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    tags = models.JSONField(default=list)  # ['array', 'hash-table', 'two-pointers']
    
    # Problem details
    input_format = models.TextField(help_text="Description of input format")
    output_format = models.TextField(help_text="Description of output format")
    constraints = models.TextField(help_text="Problem constraints")
    examples = models.JSONField(default=list)  # [{'input': '...', 'output': '...', 'explanation': '...'}]
    
    # Code templates
    python_template = models.TextField(default="def solution():\n    pass")
    javascript_template = models.TextField(default="function solution() {\n    \n}")
    java_template = models.TextField(default="class Solution {\n    public void solution() {\n        \n    }\n}")
    
    # Scoring
    max_score = models.IntegerField(default=100)
    time_limit_seconds = models.IntegerField(default=300)  # 5 minutes
    memory_limit_mb = models.IntegerField(default=256)
    
    # Metadata
    is_public = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_problems')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Statistics
    total_submissions = models.IntegerField(default=0)
    accepted_submissions = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['difficulty', 'category']),
            models.Index(fields=['is_public']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.difficulty})"
    
    @property
    def acceptance_rate(self):
        if self.total_submissions == 0:
            return 0
        return round((self.accepted_submissions / self.total_submissions) * 100, 2)


class TestCase(models.Model):
    """Test cases for coding problems"""
    problem = models.ForeignKey(CodingProblem, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.TextField()
    expected_output = models.TextField()
    is_hidden = models.BooleanField(default=False, help_text="Hidden test cases are not shown to users")
    is_sample = models.BooleanField(default=False, help_text="Sample test cases shown in problem description")
    explanation = models.TextField(blank=True)
    weight = models.IntegerField(default=1, help_text="Weight for scoring")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"TestCase #{self.id} for {self.problem.title}"


class Submission(models.Model):
    """User code submission"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('accepted', 'Accepted'),
        ('wrong_answer', 'Wrong Answer'),
        ('time_limit_exceeded', 'Time Limit Exceeded'),
        ('memory_limit_exceeded', 'Memory Limit Exceeded'),
        ('runtime_error', 'Runtime Error'),
        ('compilation_error', 'Compilation Error'),
    ]
    
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    problem = models.ForeignKey(CodingProblem, on_delete=models.CASCADE, related_name='submissions')
    
    code = models.TextField()
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    
    # Results
    score = models.IntegerField(default=0)
    passed_test_cases = models.IntegerField(default=0)
    total_test_cases = models.IntegerField(default=0)
    execution_time_ms = models.IntegerField(null=True, blank=True)
    memory_used_mb = models.FloatField(null=True, blank=True)
    
    # Error details
    error_message = models.TextField(blank=True)
    failed_test_case = models.ForeignKey(TestCase, on_delete=models.SET_NULL, null=True, blank=True, related_name='failed_submissions')
    
    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['user', 'problem']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.problem.title} ({self.status})"


class TestCaseResult(models.Model):
    """Individual test case execution result"""
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='test_results')
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    
    passed = models.BooleanField(default=False)
    actual_output = models.TextField(blank=True)
    execution_time_ms = models.IntegerField(null=True)
    memory_used_mb = models.FloatField(null=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['test_case__id']
    
    def __str__(self):
        status = "✓" if self.passed else "✗"
        return f"{status} TestCase #{self.test_case.id}"


class UserProgress(models.Model):
    """Track user progress on coding problems"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='user_progress')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coding_progress')
    problem = models.ForeignKey(CodingProblem, on_delete=models.CASCADE, related_name='user_progress')
    
    # Progress
    is_solved = models.BooleanField(default=False)
    is_attempted = models.BooleanField(default=False)
    best_score = models.IntegerField(default=0)
    attempts_count = models.IntegerField(default=0)
    
    # Best submission
    best_submission = models.ForeignKey(Submission, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    
    # Timestamps
    first_attempted_at = models.DateTimeField(null=True, blank=True)
    solved_at = models.DateTimeField(null=True, blank=True)
    last_attempted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'problem']
        indexes = [
            models.Index(fields=['user', 'is_solved']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.problem.title} ({self.best_score})"


class CodeExecutionSession(models.Model):
    """Track code execution sessions for analytics"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='code_sessions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='code_sessions')
    problem = models.ForeignKey(CodingProblem, on_delete=models.CASCADE, related_name='sessions')
    
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    total_time_seconds = models.IntegerField(default=0)
    
    submissions_count = models.IntegerField(default=0)
    successful = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Session {self.id} - {self.user.email}"
